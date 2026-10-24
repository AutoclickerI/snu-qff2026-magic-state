// Exact finite-state search. The Python entry point validates every emitted witness.
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <mutex>
#include <numeric>
#include <stdexcept>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <vector>
using namespace std;
using U = uint64_t;
using Mask = __uint128_t;
using State = array<U,4>;
using Clock = chrono::steady_clock;
struct Hash {
    size_t operator()(const State& a) const {
        U h=0x9e3779b97f4a7c15ULL;
        for (U x:a) h ^= x + 0x9e3779b97f4a7c15ULL + (h<<6) + (h>>2);
        return h;
    }
};
int n,k,extra,workers,alternatives,enumerate_circuits;
U max_class;
vector<int> cells,avail,codepos;
vector<pair<int,int>> edges;
vector<U> touched;
vector<Mask> commute,lower;
vector<State> states;
vector<vector<int>> adj;
vector<int> dist,initial;
vector<vector<int>> moves;
int min_cx,min_depth,min_depth_cx;

State canonical(State s) {
    for(int i=0;i<k;i++) {
        int j=i;
        for(int t=i+1;t<k;t++) if(countr_zero(s[t])<countr_zero(s[j])) j=t;
        swap(s[i],s[j]);
        U bit=s[i]&-s[i];
        for(int t=0;t<k;t++) if(t!=i && (s[t]&bit)) s[t]^=s[i];
    }
    return s;
}
bool coordinate(const State& s) {
    for(int i=0;i<k;i++) if(!has_single_bit(s[i])) return false;
    return true;
}
void build_graph() {
    static const int gens[4][4]={{0,2,4,6},{1,2,5,6},{3,4,5,6},{0,1,2,-1}};
    State target{};
    for(int i=0;i<k;i++) for(int j:gens[i]) if(j>=0)
        target[i] |= U(1)<< (find(avail.begin(),avail.end(),cells[j])-avail.begin());
    target=canonical(target);
    unordered_map<State,int,Hash> ids;
    ids.emplace(target,0); states.push_back(target); dist.push_back(0);
    for(size_t i=0;i<states.size();i++) {
        State s=states[i]; vector<int> row;
        if(coordinate(s)) initial.push_back(i);
        for(auto [c,t]:edges) {
            State ns=s;
            for(int r=0;r<k;r++) if(ns[r]&(U(1)<<c)) ns[r]^=U(1)<<t;
            ns=canonical(ns);
            auto [it,inserted]=ids.emplace(ns,states.size());
            int next=it->second;
            if(inserted) { states.push_back(ns); dist.push_back(dist[i]+1); }
            row.push_back(next);
        }
        adj.push_back(move(row));
    }
    min_cx=numeric_limits<int>::max();
    for(int s:initial) min_cx=min(min_cx,dist[s]);
    cerr<<"graph complete: "<<states.size()<<" states, "<<initial.size()
        <<" coordinate states, minimum CX "<<min_cx<<"\n";
}
void build_moves(int start,U used,vector<int>& path) {
    for(int e=start;e<(int)edges.size();e++) if(!(used&touched[e])) {
        path.push_back(e); moves.push_back(path);
        build_moves(e+1,used|touched[e],path);
        path.pop_back();
    }
}

struct Circuit {
    vector<vector<int>> layers;
    vector<int> pivots;
    array<int,8> vec{};
    int units=0,cx=0;
};
bool better(const Circuit& a,const Circuit& b) {
    // A pure logical Z fault contributes at first order; the other bins need
    // a second data error. Keep this lane's candidate ordering sensitive to
    // that distinction. The full judge/MC still determines circuit ranking.
    return tuple(a.vec[0],a.units,a.layers.size(),a.cx,a.pivots,a.layers) <
           tuple(b.vec[0],b.units,b.layers.size(),b.cx,b.pivots,b.layers);
}
// A lookup table over suffix-propagated Z syndrome/parity and X syndrome.
array<array<uint8_t,8>,16384> gate_weights;
bool dangerous(int z,int x) { return x==0 && bool(z&8)!=bool(z&7); }
int table_index(int zu,int zv,int xu,int xv) {return (((zu*16+zv)*8+xu)*8+xv);}
void build_weights() {
    for(int zu=0;zu<16;zu++) for(int zv=0;zv<16;zv++)
        for(int xu=0;xu<8;xu++) for(int xv=0;xv<8;xv++) {
            auto& a=gate_weights[table_index(zu,zv,xu,xv)];
            for(int pu=0;pu<4;pu++) for(int pv=0;pv<4;pv++) if(pu||pv) {
                int z=((pu&2)?zu:0)^((pv&2)?zv:0);
                int x=((pu&1)?xu:0)^((pv&1)?xv:0);
                if(dangerous(z,x)) a[z&7]++;
            }
        }
}
void score(Circuit& c) {
    int T=c.layers.size();
    array<int,36> first,last,z{},x{};
    first.fill(T);last.fill(-1);
    c.vec.fill(0);c.cx=0;
    for(int t=0;t<T;t++) for(int e:c.layers[t]) {
        c.cx++;auto [u,v]=edges[e];
        first[u]=min(first[u],t);first[v]=min(first[v],t);last[u]=last[v]=t;
    }
    for(int q=0;q<n;q++) if(codepos[q]>=0) {
        if(first[q]==T) first[q]=0;
        z[q]=(codepos[q]+1)|8;x[q]=codepos[q]+1;
    }
    auto add=[&](int zz,int xx,int w){if(dangerous(zz,xx)) c.vec[zz&7]+=w;};
    for(int t=T-1;t>=0;t--) {
        U busy=0;
        for(int e:c.layers[t]) {
            auto [u,v]=edges[e];busy|=touched[e];
            const auto& a=gate_weights[table_index(z[u],z[v],x[u],x[v])];
            for(int j=0;j<8;j++) c.vec[j]+=a[j];
        }
        for(int q=0;q<n;q++) if(!(busy&(U(1)<<q)) && first[q]<t &&
                                   (codepos[q]>=0 || t<=last[q])) {
            add(0,x[q],5);add(z[q],0,5);add(z[q],x[q],5);
        }
        for(int e:c.layers[t]) {auto [u,v]=edges[e];z[v]^=z[u];x[u]^=x[v];}
        for(int q:c.pivots) if(first[q]==t) add(z[q],0,15);
    }
    if(T==0) for(int q:c.pivots) add(z[q],0,15);
    c.units=accumulate(c.vec.begin(),c.vec.end(),0);
}
Circuit depth_proof() {
    vector<int> path;build_moves(0,0,path);
    vector<int> dd(states.size(),-1),cost(states.size(),numeric_limits<int>::max());
    vector<int> parent(states.size(),-1),via(states.size(),-1),front{0};
    dd[0]=0;cost[0]=0;
    int best=-1;
    for(int depth=0;!front.empty();depth++) {
        for(int s:front) if(coordinate(states[s]) && (best<0 || cost[s]<cost[best])) best=s;
        if(best>=0) {min_depth=depth;min_depth_cx=cost[best];break;}
        vector<int> next;
        for(int s:front) for(int m=0;m<(int)moves.size();m++) {
            int v=s;for(int e:moves[m]) v=adj[v][e];
            if(dd[v]<0) {dd[v]=depth+1;next.push_back(v);}
            if(dd[v]==depth+1 && cost[v]>cost[s]+(int)moves[m].size()) {
                cost[v]=cost[s]+moves[m].size();parent[v]=s;via[v]=m;
            }
        }
        front=move(next);
    }
    if(best<0) throw runtime_error("Layer BFS failed despite reachable coordinate state");
    Circuit c;
    for(int i=0;i<k;i++) c.pivots.push_back(countr_zero(states[best][i]));
    for(int s=best;s!=0;s=parent[s]) c.layers.push_back(moves[via[s]]);
    score(c);
    cerr<<"layer BFS complete: minimum depth "<<min_depth<<", CX at that depth "
        <<min_depth_cx<<", "<<moves.size()<<" legal nonempty layers\n";
    return c;
}

struct CountKey { int state,left;Mask sleep;bool operator==(const CountKey&) const=default; };
struct CountHash {
    size_t operator()(const CountKey& a) const {
        U h=(U(a.state)*2654435761U)^U(a.left);
        h^=U(a.sleep)+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2);
        h^=U(a.sleep>>64)+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2);return h;
    }
};
U checked_add(U a,U b) {
    if(numeric_limits<U>::max()-a<b) throw runtime_error("Circuit count overflow (not truncated)");
    return a+b;
}
unordered_map<CountKey,U,CountHash> count_cache;
U count_paths(int s,int left,Mask sleep) {
    if(dist[s]>left) return 0;
    if(left==0) return s==0;
    CountKey key{s,left,sleep};
    auto it=count_cache.find(key);if(it!=count_cache.end()) return it->second;
    U count=0;
    for(int e=0;e<(int)edges.size();e++) if(!(sleep&(Mask(1)<<e))) {
        int v=adj[s][e];if(dist[v]>left-1) continue;
        count=checked_add(count,count_paths(v,left-1,(sleep|lower[e])&commute[e]));
    }
    count_cache.emplace(key,count);return count;
}
struct Stats {
    U count=0;
    Circuit best;
};
using ClassKey=tuple<int,int,int>; // CX, depth, 0=ASAP, 1=alternative
struct Collector {
    map<ClassKey,Stats> stats;
    vector<Circuit> top,samples;
    void record(Circuit& c,int mode) {
        score(c);
        auto& s=stats[{c.cx,(int)c.layers.size(),mode}];
        if(s.count==0 || better(c,s.best)) s.best=c;
        s.count++;
        if(samples.size()<8) samples.push_back(c);
        if(top.size()<20 || better(c,top.back())) {
            auto it=lower_bound(top.begin(),top.end(),c,better);
            if(it==top.end() || it->pivots!=c.pivots || it->layers!=c.layers) top.insert(it,c);
            if(top.size()>20) top.pop_back();
        }
    }
};
struct Enumerator {
    Collector& out;
    vector<int> path,pivots;
    U leaves=0;
    void alternative_schedules(const Circuit& asap) {
        int m=path.size(),bound=min_depth+1;
        if((int)asap.layers.size()>bound || m==0) return;
        vector<array<int,2>> pred(m);
        array<int,36> last;last.fill(-1);
        vector<int> latest(m,bound-1),assigned(m,-1),asap_time(m);
        for(int i=0;i<m;i++) {
            auto [u,v]=edges[path[i]];pred[i]={last[u],last[v]};last[u]=last[v]=i;
            asap_time[i]=0;
            for(int p:pred[i]) if(p>=0) asap_time[i]=max(asap_time[i],asap_time[p]+1);
        }
        for(int i=m-1;i>=0;i--) for(int p:pred[i]) if(p>=0) latest[p]=min(latest[p],latest[i]-1);
        vector<vector<int>> scheduled(bound);
        function<void(int,bool)> visit=[&](int i,bool differs) {
            if(i==m) {
                if(!differs) return;
                int depth=bound;
                while(depth && scheduled[depth-1].empty()) depth--;
                for(int t=0;t<depth;t++) if(scheduled[t].empty()) return;
                Circuit c;c.pivots=pivots;
                c.layers.assign(scheduled.begin(),scheduled.begin()+depth);
                for(auto& layer:c.layers) sort(layer.begin(),layer.end());
                out.record(c,1);return;
            }
            int earliest=0;for(int p:pred[i]) if(p>=0) earliest=max(earliest,assigned[p]+1);
            for(int t=earliest;t<=latest[i];t++) {
                assigned[i]=t;scheduled[t].push_back(path[i]);
                visit(i+1,differs || t!=asap_time[i]);scheduled[t].pop_back();
            }
        };
        visit(0,false);
    }
    void leaf() {
        leaves++;Circuit c;c.pivots=pivots;
        array<int,36> ready{};
        for(int e:path) {
            auto [u,v]=edges[e];int t=max(ready[u],ready[v]);
            if(t>=(int)c.layers.size()) c.layers.resize(t+1);
            c.layers[t].push_back(e);ready[u]=ready[v]=t+1;
        }
        for(auto& layer:c.layers) sort(layer.begin(),layer.end());
        out.record(c,0);
        if(alternatives) alternative_schedules(c);
    }
    void dfs(int s,int left,Mask sleep) {
        if(left==0) {if(s==0) leaf();return;}
        for(int e=0;e<(int)edges.size();e++) if(!(sleep&(Mask(1)<<e))) {
            int v=adj[s][e];if(dist[v]>left-1) continue;
            path.push_back(e);dfs(v,left-1,(sleep|lower[e])&commute[e]);path.pop_back();
        }
    }
};
void write_circuit(const Circuit& c) {
    cout<<"{\"ops\":[";
    for(size_t t=0;t<c.layers.size();t++) {
        if(t) cout<<',';
        cout<<'[';
        for(size_t j=0;j<c.layers[t].size();j++) {
            if(j) cout<<',';
            auto [u,v]=edges[c.layers[t][j]];
            cout<<'['<<avail[u]<<','<<avail[v]<<']';
        }
        cout<<']';
    }
    cout<<"],\"pivots\":[";
    for(size_t j=0;j<c.pivots.size();j++) {if(j) cout<<',';cout<<avail[c.pivots[j]];}
    cout<<"],\"danger_units\":"<<c.units<<",\"danger_vector_units\":[";
    for(int j=0;j<8;j++) {if(j) cout<<',';cout<<c.vec[j];}
    cout<<"]}";
}
int main() {try {
    auto began=Clock::now();
    if(!(cin>>n>>k>>extra>>workers>>alternatives>>enumerate_circuits>>max_class))
        throw runtime_error("Invalid input");
    if(n<7 || n>36 || (k!=3 && k!=4) || workers<1 || workers>16)
        throw runtime_error("Invalid dimensions/workers");
    for(int i=0,q;i<n;i++) {cin>>q;avail.push_back(q);if(i<7) cells.push_back(q);}
    sort(avail.begin(),avail.end());codepos.resize(n,-1);
    for(int i=0;i<7;i++) codepos[find(avail.begin(),avail.end(),cells[i])-avail.begin()]=i;
    for(int u=0;u<n;u++) for(int v=0;v<n;v++)
        if(abs(avail[u]/6-avail[v]/6)+abs(avail[u]%6-avail[v]%6)==1) {
            edges.emplace_back(u,v);touched.push_back((U(1)<<u)|(U(1)<<v));
        }
    if(edges.size()>128) throw runtime_error("Too many oriented edges");
    commute.resize(edges.size());lower.resize(edges.size());
    for(int e=0;e<(int)edges.size();e++) {
        lower[e]=(Mask(1)<<e)-1;
        for(int f=0;f<(int)edges.size();f++) if(!(touched[e]&touched[f])) commute[e]|=Mask(1)<<f;
    }
    build_weights();build_graph();
    if(initial.empty()) {cout<<"{\"unreachable\":true,\"states\":"<<states.size()<<"}\n";return 0;}
    Circuit depth_best=depth_proof();
    vector<U> counts(extra+1),algebraic_counts(extra+1),enumerated(extra+1);
    vector<bool> skip(extra+1,false);
    if(enumerate_circuits) for(int d=0;d<=extra;d++) {
        for(int s:initial) counts[d]=checked_add(counts[d],count_paths(s,min_cx+d,0));
        skip[d]=max_class && counts[d]>max_class;
        cerr<<"CX "<<min_cx+d<<": "<<counts[d]<<" disjoint-commutation classes"
            <<(skip[d]?"; skipped by explicit class limit":"; will enumerate all")<<"\n";
    }
    count_cache.clear();count_cache.rehash(0);
    // Count the larger algebraic equivalence classes too. Shared-control or
    // shared-target swaps are NOT removed from noisy-circuit evaluation.
    auto physical_commute=commute;
    fill(commute.begin(),commute.end(),0);
    for(int e=0;e<(int)edges.size();e++) for(int f=0;f<(int)edges.size();f++)
        if(e!=f && edges[e].first!=edges[f].second && edges[e].second!=edges[f].first)
            commute[e]|=Mask(1)<<f;
    if(enumerate_circuits) for(int d=0;d<=extra;d++) {
        for(int s:initial) algebraic_counts[d]=checked_add(algebraic_counts[d],count_paths(s,min_cx+d,0));
        cerr<<"CX "<<min_cx+d<<": "<<algebraic_counts[d]<<" algebraic commutation classes\n";
    }
    count_cache.clear();count_cache.rehash(0);
    commute=move(physical_commute);
    vector<pair<int,int>> tasks;
    if(enumerate_circuits) for(int d=0;d<=extra;d++) if(!skip[d])
        for(int s:initial) if(dist[s]<=min_cx+d) tasks.emplace_back(d,s);
    atomic<size_t> next{0};mutex log_mutex;
    vector<Collector> collectors(workers);vector<thread> threads;
    vector<vector<U>> leafcounts(workers,vector<U>(extra+1));
    for(int w=0;w<workers;w++) threads.emplace_back([&,w] {
        while(true) {
            size_t task=next.fetch_add(1);if(task>=tasks.size()) break;
            auto [d,s]=tasks[task];Enumerator e{collectors[w],{},{},0};
            for(int i=0;i<k;i++) e.pivots.push_back(countr_zero(states[s][i]));
            e.dfs(s,min_cx+d,0);leafcounts[w][d]+=e.leaves;
            lock_guard<mutex> lock(log_mutex);
            cerr<<"completed task "<<task+1<<'/'<<tasks.size()<<", CX "<<min_cx+d
                <<", pivot state "<<s<<", circuits "<<e.leaves<<"\n";
        }
    });
    for(auto& t:threads) t.join();
    Collector merged;
    for(int w=0;w<workers;w++) {
        for(int d=0;d<=extra;d++) enumerated[d]+=leafcounts[w][d];
        for(auto& [key,s]:collectors[w].stats) {
            auto& dst=merged.stats[key];
            if(dst.count==0 || better(s.best,dst.best)) dst.best=s.best;
            dst.count+=s.count;
        }
        for(auto& c:collectors[w].top) merged.top.push_back(c);
        for(auto& c:collectors[w].samples) merged.samples.push_back(c);
    }
    for(int d=0;d<=extra;d++) if(enumerate_circuits && !skip[d] && enumerated[d]!=counts[d])
        throw runtime_error("Enumeration/count-DP disagreement");
    sort(merged.top.begin(),merged.top.end(),better);
    merged.top.erase(unique(merged.top.begin(),merged.top.end(),[](const Circuit& a,const Circuit& b){
        return a.pivots==b.pivots && a.layers==b.layers;
    }),merged.top.end());
    if(merged.top.size()>20) merged.top.resize(20);
    cout<<"{\"states\":"<<states.size()<<",\"oriented_edges\":"<<edges.size()
        <<",\"legal_layers\":"<<moves.size()<<",\"coordinate_states\":"<<initial.size()
        <<",\"min_cx\":"<<min_cx<<",\"min_depth\":"<<min_depth
        <<",\"min_depth_cx\":"<<min_depth_cx<<",\"alternative_depth_bound\":"<<min_depth+1
        <<",\"alternatives\":"<<(alternatives?"true":"false")
        <<",\"enumeration_requested\":"<<(enumerate_circuits?"true":"false")
        <<",\"counted_classes\":[";
    for(int d=0;enumerate_circuits && d<=extra;d++) {if(d) cout<<',';
        cout<<"{\"cx\":"<<min_cx+d<<",\"total\":"<<counts[d]
            <<",\"algebraic_commutation_classes\":"<<algebraic_counts[d]<<",\"enumerated\":"<<enumerated[d]
            <<",\"complete\":"<<((enumerate_circuits&&!skip[d])?"true":"false")<<'}';}
    cout<<"],\"distance_histogram\":[";
    vector<U> hist(*max_element(dist.begin(),dist.end())+1);
    for(int d:dist) hist[d]++;
    for(size_t d=0;d<hist.size();d++) {if(d) cout<<',';cout<<hist[d];}
    cout<<"],\"depth_optimal\":";write_circuit(depth_best);
    cout<<",\"classes\":[";bool first=true;
    for(auto& [key,s]:merged.stats) {
        if(!first) cout<<',';
        first=false;auto [cx,depth,mode]=key;
        cout<<"{\"cx\":"<<cx<<",\"depth\":"<<depth<<",\"mode\":\""
            <<(mode?"alternative":"ASAP")<<"\",\"count\":"<<s.count<<",\"best\":";
        write_circuit(s.best);cout<<'}';
    }
    cout<<"],\"top\":[";
    for(size_t i=0;i<merged.top.size();i++) {if(i) cout<<',';write_circuit(merged.top[i]);}
    cout<<"],\"verification_samples\":[";
    for(size_t i=0;i<merged.samples.size();i++) {if(i) cout<<',';write_circuit(merged.samples[i]);}
    cout<<"],\"engine_seconds\":"<<chrono::duration<double>(Clock::now()-began).count()<<"}\n";
}catch(const exception& e){cerr<<"ERROR: "<<e.what()<<'\n';return 1;}}
