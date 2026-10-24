// Time-layered exhaustive search of block-A encoders on v36c's exterior (windows from releases and D->A ticks).
// Scores every complete encoder by the first-order in-situ class cost kappa[c] (from evalx table), keeps top K.
// stdin: 128 kappa values, 128 alpha values, then: maxcx K pivotmask(-1 = all) tmin tmax
//        then 7 lines: REL DA mr_ok (per code position)
// stdout: JSON lines {score, acc, pivots, layers:[[t,c,tg]...], init:[...]} best first.
#include <bits/stdc++.h>
using namespace std;
typedef uint32_t u32;
static const int NQ = 7;
// code-position edges (A cells [1,14,8,9,2,16,15]): 1-2,2-8,8-9,8-14,9-15,14-15,15-16
static const int UE[7][2] = {{0,4},{4,2},{2,3},{2,1},{3,6},{1,6},{6,5}};
static const int HAMS[3] = {0b1010101, 0b1100110, 0b1111000};
double kappa[128], alpha_[128];
int REL[NQ], DA[NQ], ZMR[NQ], PMR[NQ];
int maxcx, K, TMIN, TMAX;
double P = 1e-3;

int syn(int b){int s=0; for(int k=0;k<3;k++) if(__builtin_popcount(b&HAMS[k])&1) s|=1<<k; return s;}
int clsf(int ex,int ez){int l=__builtin_popcount(ez&7)&1; return syn(ex)|(syn(ez)<<3)|(l<<6);}

typedef array<uint8_t,4> Sp;   // 4 vectors (7-bit)
u32 canon(Sp s){
    // RREF by highest bit
    int v[4]={s[0],s[1],s[2],s[3]};
    int r=0;
    for(int b=NQ-1;b>=0 && r<4;b--){
        int p=-1; for(int i=r;i<4;i++) if(v[i]>>b&1){p=i;break;}
        if(p<0) continue; swap(v[r],v[p]);
        for(int i=0;i<4;i++) if(i!=r && (v[i]>>b&1)) v[i]^=v[r];
        r++;
    }
    sort(v,v+4);
    return (u32)v[0]|((u32)v[1]<<7)|((u32)v[2]<<14)|((u32)v[3]<<21);
}
struct Gate{int c,t;};
vector<vector<Gate>> matchings;
void build_matchings(){
    // all sets of disjoint undirected edges, with all orientations
    for(int m=0;m<(1<<7);m++){
        int used=0; bool ok=true;
        for(int e=0;e<7;e++) if(m>>e&1){int a=UE[e][0],b=UE[e][1]; if(used>>a&1 || used>>b&1){ok=false;break;} used|=1<<a|1<<b;}
        if(!ok) continue;
        vector<int> es; for(int e=0;e<7;e++) if(m>>e&1) es.push_back(e);
        int ne=es.size();
        for(int o=0;o<(1<<ne);o++){
            vector<Gate> g;
            for(int i=0;i<ne;i++){int a=UE[es[i]][0],b=UE[es[i]][1]; if(o>>i&1) g.push_back({b,a}); else g.push_back({a,b});}
            matchings.push_back(g);
        }
    }
}
Sp app(Sp s,const vector<Gate>& g){
    for(auto&x:g) for(int i=0;i<4;i++) if(s[i]>>x.c&1) s[i]^=1<<x.t;
    return s;
}
u32 TARGET;
// per pivot set
int pivmask;
int earliest[NQ], latest[NQ];
vector<unordered_map<u32,char>> reach;  // reach[t-TMIN][canon] : can reach target by end of TMAX
struct Rec{double score,acc; vector<array<int,3>> layers; int pivots; int cx; vector<array<int,2>> init;};
struct Cmp{bool operator()(const Rec&a,const Rec&b)const{return a.score<b.score;}};
priority_queue<Rec,vector<Rec>,Cmp> best;   // max-heap of the K best (lowest) scores
long long leaves=0, nodes=0;
vector<vector<Gate>> path;  // layers chosen per tick

bool usable(const vector<Gate>& g,int t){
    for(auto&x:g){ if(t<earliest[x.c]||t>latest[x.c]||t<earliest[x.t]||t>latest[x.t]) return false; }
    return true;
}
bool reach_at(int t,u32 c){
    if(t>TMAX) return c==TARGET;
    auto&m=reach[t-TMIN]; auto it=m.find(c); return it!=m.end() && it->second;
}
// build reach tables by forward BFS of states then backward marking
void build_reach(Sp init){
    int T=TMAX-TMIN+1;
    vector<unordered_map<u32,Sp>> lv(T+1);
    lv[0][canon(init)]=init;
    for(int t=TMIN;t<=TMAX;t++){
        auto& cur=lv[t-TMIN]; auto& nx=lv[t-TMIN+1];
        for(auto& [k,s]:cur) for(auto& g:matchings) if(usable(g,t)){ Sp n=app(s,g); u32 c=canon(n); if(!nx.count(c)) nx[c]=n; }
    }
    reach.assign(T,{});
    // backward
    vector<unordered_map<u32,char>> ok(T+1);
    for(auto&[k,s]:lv[T]) ok[T][k]=(k==TARGET);
    for(int t=TMAX;t>=TMIN;t--){
        auto& cur=lv[t-TMIN];
        for(auto&[k,s]:cur){
            char r=0;
            for(auto& g:matchings) if(usable(g,t)){ Sp n=app(s,g); u32 c=canon(n); auto it=ok[t-TMIN+1].find(c); if(it!=ok[t-TMIN+1].end()&&it->second){r=1;break;} }
            ok[t-TMIN][k]=r;
        }
    }
    for(int t=TMIN;t<=TMAX;t++) reach[t-TMIN]=ok[t-TMIN];
}

// first-order score of a complete circuit
void score_circuit(){
    // layers path[t-TMIN]
    int xc[NQ],zc[NQ];
    for(int i=0;i<NQ;i++){xc[i]=clsf(1<<i,0); zc[i]=clsf(0,1<<i);}
    int fg[NQ], lg[NQ]; for(int i=0;i<NQ;i++){fg[i]=99; lg[i]=-1;}
    int cx=0;
    for(int t=TMIN;t<=TMAX;t++) for(auto&g:path[t-TMIN]){ cx++; for(int q:{g.c,g.t}){fg[q]=min(fg[q],t); lg[q]=max(lg[q],t);} }
    for(int i=0;i<NQ;i++) if(fg[i]==99) return;   // every cell must be touched
    double sc=0, ac=0;
    // init choice per cell: pivot -> RX at fg-1 (or RX+check if fg-2>REL: cost (2/3)), Z input -> MR if fg==REL+1 & MROK, else R at fg-1
    // busy ticks per cell (for idles): init tick(s), gates
    // backward pass
    int initT[NQ]; int kind[NQ]; // 0 reuse (Z: after ZMR measurement, pivot: after MX release), 1 R, 2 RX
    for(int q=0;q<NQ;q++){
        bool piv=pivmask>>q&1;
        double best_m=1e9; int bk=-1, bt=0;
        if(piv){
            if(fg[q]-1>REL[q]){ best_m=1.0; bk=2; bt=fg[q]-1; }
            if(PMR[q]){ double m2=(2.0/3)*(1+fg[q]-REL[q]-1); if(m2<best_m){best_m=m2; bk=0; bt=REL[q];} }
        } else {
            if(fg[q]-1>REL[q]){ best_m=1.0; bk=1; bt=fg[q]-1; }
            if(ZMR[q]>=0 && fg[q]>ZMR[q]){ double m2=(2.0/3)*(1+fg[q]-ZMR[q]-1); if(m2<best_m){best_m=m2; bk=0; bt=ZMR[q];} }
        }
        if(bk<0) return;
        kind[q]=bk; initT[q]=bt;
    }
    vector<vector<char>> busy(TMAX+2, vector<char>(NQ,0));
    for(int t=TMIN;t<=TMAX;t++) for(auto&g:path[t-TMIN]){busy[t][g.c]=1;busy[t][g.t]=1;}
    for(int t=TMAX;t>=TMIN-1;t--){
        // frames now = just after tick t
        if(t>=TMIN){
            for(auto&g:path[t-TMIN]){
                for(int a=0;a<4;a++) for(int b=0;b<4;b++){ if(!a&&!b) continue;
                    int c=0; if(a&1) c^=xc[g.c]; if(a&2) c^=zc[g.c]; if(b&1) c^=xc[g.t]; if(b&2) c^=zc[g.t];
                    sc+=P/15*kappa[c]; ac+=P/15*alpha_[c]; }
            }
            for(int q=0;q<NQ;q++){
                if(busy[t][q]) continue;
                if(t>=DA[q]) continue;
                bool live = t>initT[q];
                if(!live) continue;
                double w=P/3; int c1=xc[q],c2=zc[q],c3=xc[q]^zc[q];
                sc+=w*(kappa[c1]+kappa[c2]+kappa[c3]); ac+=w*(alpha_[c1]+alpha_[c2]+alpha_[c3]);
            }
        }
        // init faults at tick t (frames just after tick t)
        for(int q=0;q<NQ;q++){
            if(initT[q]!=t) continue;
            if(kind[q]==0){ double w=P/3; int c1=xc[q],c2=zc[q],c3=xc[q]^zc[q]; sc+=w*(kappa[c1]+kappa[c2]+kappa[c3]); ac+=w*(alpha_[c1]+alpha_[c2]+alpha_[c3]); }
            else if(kind[q]==1){ sc+=P*kappa[xc[q]]; ac+=P*alpha_[xc[q]]; }
            else { sc+=P*kappa[zc[q]]; ac+=P*alpha_[zc[q]]; }
        }
        if(t<TMIN) break;
        // undo layer t (frames -> just before tick t)
        for(auto&g:path[t-TMIN]){ xc[g.c]^=xc[g.t]; zc[g.t]^=zc[g.c]; }
    }
    leaves++;
    if((int)best.size()<K || sc<best.top().score){
        Rec r; r.score=sc; r.acc=ac; r.pivots=pivmask; r.cx=cx; for(int q=0;q<NQ;q++) r.init.push_back({kind[q],initT[q]});
        for(int t=TMIN;t<=TMAX;t++) for(auto&g:path[t-TMIN]) r.layers.push_back({t,g.c,g.t});
        best.push(r); if((int)best.size()>K) best.pop();
    }
}
int cxcount=0;
void dfs(int t,Sp s){
    nodes++;
    if(t>TMAX){ if(canon(s)==TARGET) score_circuit(); return; }
    u32 cs=canon(s);
    for(auto& g:matchings){
        if(!usable(g,t)) continue;
        if(cxcount+(int)g.size()>maxcx) continue;
        // no-op pruning: each gate alone must change the span
        bool noop=false;
        for(auto&x:g){ vector<Gate> one{x}; if(canon(app(s,one))==cs){noop=true;break;} }
        if(noop) continue;
        Sp n=app(s,g);
        if(!reach_at(t+1,canon(n))) continue;
        path[t-TMIN]=g; cxcount+=g.size();
        dfs(t+1,n);
        cxcount-=g.size(); path[t-TMIN].clear();
    }
}
int main(){
    for(int i=0;i<128;i++) cin>>kappa[i];
    for(int i=0;i<128;i++) cin>>alpha_[i];
    int pm; cin>>maxcx>>K>>pm>>TMIN>>TMAX;
    for(int i=0;i<NQ;i++) cin>>REL[i]>>DA[i]>>ZMR[i]>>PMR[i];
    build_matchings();
    {Sp t{}; t[0]=HAMS[0]; t[1]=HAMS[1]; t[2]=HAMS[2]; t[3]=0b0000111; TARGET=canon(t);}
    path.assign(TMAX-TMIN+1,{});
    vector<Rec> all;
    for(int m=0;m<(1<<NQ);m++){
        if(__builtin_popcount(m)!=4) continue;
        if(pm>=0 && m!=pm) continue;
        pivmask=m;
        for(int q=0;q<NQ;q++){
            bool piv=m>>q&1;
            earliest[q]= piv ? (PMR[q] ? REL[q]+1 : REL[q]+2) : (ZMR[q]>=0 ? min(ZMR[q]+1,REL[q]+2) : REL[q]+2);
            latest[q]=DA[q]-1;
        }
        Sp init{}; int k=0; for(int q=0;q<NQ;q++) if(m>>q&1) init[k++]=1<<q;
        build_reach(init);
        if(!reach_at(TMIN,canon(init))) { cerr<<"pivots "<<m<<" unreachable\n"; continue; }
        long long l0=leaves;
        dfs(TMIN,init);
        cerr<<"pivots "<<m<<" leaves "<<leaves-l0<<" nodes "<<nodes<<"\n";
    }
    while(!best.empty()){all.push_back(best.top()); best.pop();}
    reverse(all.begin(),all.end());
    cout<<setprecision(12);
    for(auto&r:all){
        cout<<"{\"score\":"<<r.score<<",\"acc\":"<<r.acc<<",\"pivots\":"<<r.pivots<<",\"cx\":"<<r.cx<<",\"layers\":[";
        for(size_t i=0;i<r.layers.size();i++){ if(i) cout<<","; cout<<"["<<r.layers[i][0]<<","<<r.layers[i][1]<<","<<r.layers[i][2]<<"]"; }
        cout<<"],\"init\":[";
        for(int q=0;q<NQ;q++){ if(q) cout<<","; cout<<"["<<r.init[q][0]<<","<<r.init[q][1]<<"]"; }
        cout<<"]}\n";
    }
    cerr<<"total leaves "<<leaves<<"\n";
}
