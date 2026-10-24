#include <array>
#include <algorithm>
#include <bit>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>
using namespace std;using S=array<unsigned,7>;
struct Hash{size_t operator()(const S&s)const{size_t h=0;for(auto x:s)h=h*137+x;return h;}};
S canon(S s,int k){for(int i=0;i<k;i++){int j=i;for(int t=i+1;t<k;t++)if(countr_zero(s[t])<countr_zero(s[j]))j=t;swap(s[i],s[j]);unsigned bit=s[i]&-s[i];for(int t=0;t<k;t++)if(t!=i&&(s[t]&bit))s[t]^=s[i];}return s;}
vector<int>cells={1,14,8,9,2,16,15};vector<pair<int,int>>edges;vector<vector<int>>layers(1);vector<unsigned>masks(1,0);
struct Graph{int k;vector<S>states;unordered_map<S,int,Hash>ids;vector<vector<int>>adj,next;vector<array<int,7>>measure,rx;};
Graph make(int k){Graph g;g.k=k;S init{};for(int j=0;j<k;j++)init[j]=1u<<j;if(k==4)init={85,102,120,7,0,0,0};init=canon(init,k);g.states.push_back(init);g.ids[init]=0;
 for(size_t i=0;i<g.states.size();i++){vector<int>row;for(auto[c,t]:edges){S ns=g.states[i];for(int j=0;j<k;j++)if(ns[j]>>c&1)ns[j]^=1u<<t;ns=canon(ns,k);if(!g.ids.count(ns)){g.ids[ns]=g.states.size();g.states.push_back(ns);}row.push_back(g.ids[ns]);}g.adj.push_back(row);}
 g.next.resize(g.states.size(),vector<int>(layers.size()));for(int i=0;i<(int)g.states.size();i++)for(int l=0;l<(int)layers.size();l++){int s=i;for(int e:layers[l])s=g.adj[s][e];g.next[i][l]=s;}return g;}
int main(){
 vector<unsigned>touch;for(int a=0;a<7;a++)for(int b=0;b<7;b++)if(abs(cells[a]/6-cells[b]/6)+abs(cells[a]%6-cells[b]%6)==1){edges.push_back({a,b});touch.push_back((1u<<a)|(1u<<b));}
 vector<int>path;function<void(int,unsigned)>gen=[&](int e0,unsigned used){for(int e=e0;e<(int)edges.size();e++)if(!(touch[e]&used)){path.push_back(e);layers.push_back(path);masks.push_back(used|touch[e]);gen(e+1,used|touch[e]);path.pop_back();}};gen(0,0);
 array<Graph,6>g;for(int k=3;k<=5;k++){g[k]=make(k);cerr<<"rank "<<k<<" states "<<g[k].states.size()<<"\n";}
 for(int k=3;k<=5;k++){g[k].measure.resize(g[k].states.size());g[k].rx.resize(g[k].states.size());for(int i=0;i<(int)g[k].states.size();i++)for(int q=0;q<7;q++){
  g[k].measure[i][q]=g[k].rx[i][q]=-1;S s=g[k].states[i];int pivot=-1;for(int j=0;j<k;j++)if(s[j]>>q&1){pivot=j;break;}
  if(pivot>=0&&k>3){for(int j=0;j<k;j++)if(j!=pivot&&(s[j]>>q&1))s[j]^=s[pivot];s[pivot]=s[k-1];s[k-1]=0;g[k].measure[i][q]=g[k-1].ids.at(canon(s,k-1));}
  if(pivot<0&&k<5){s[k]=1u<<q;g[k].rx[i][q]=g[k+1].ids.at(canon(s,k+1));}
 }}
 int jobs;cin>>jobs;cout<<"[";bool first=true;
 for(int job=0;job<jobs;job++){
  int family,mode,R;cin>>family>>mode>>R;array<int,7>rx,rz;for(auto&x:rx)cin>>x;for(auto&x:rz)cin>>x;
  vector<int>rank=family==5?vector<int>{5,4}:vector<int>{4,3,4};int stages=rank.size();vector<int>off(stages+1,0);for(int a=0;a<stages;a++)off[a+1]=off[a]+g[rank[a]].states.size();int N=off.back(),goal=off[stages-1];
  for(unsigned piv=0;piv<128;piv++)if(popcount(piv)==family){S init{};array<int,7>ready;int x=0;for(int q=0;q<7;q++){if(piv>>q&1)init[x++]=1u<<q;ready[q]=(piv>>q&1)?rx[q]:rz[q];}int start=g[family].ids.at(canon(init,family));int begin=*min_element(ready.begin(),ready.end());
   vector<int>cost(N,9999),ncost(N),prev((R+1)*N,-1);vector<short>action((R+1)*N,-1);cost[start]=0;
   for(int t=begin;t<R;t++){
    fill(ncost.begin(),ncost.end(),9999);unsigned avail=0;for(int q=0;q<7;q++)if(ready[q]<=t)avail|=1u<<q;vector<int>ls;for(int l=0;l<(int)layers.size();l++)if((masks[l]&avail)==masks[l])ls.push_back(l);
    auto put=[&](int dst,int src,int value,int a){if(value<ncost[dst]){ncost[dst]=value;prev[(t+1)*N+dst]=src;action[(t+1)*N+dst]=a;}};
    for(int a=0;a<stages;a++)for(int s=0;s<(int)g[rank[a]].states.size();s++){int src=off[a]+s;if(cost[src]>=9999)continue;for(int l:ls){int ns=g[rank[a]].next[s][l],val=cost[src]+10*layers[l].size();put(off[a]+ns,src,val,l*8+7);
      if(a+1<stages)for(int q=0;q<7;q++)if((avail>>q&1)&&!(masks[l]>>q&1)){int dst=a==0?g[rank[a]].measure[ns][q]:g[rank[a]].rx[ns][q];if(dst>=0)put(off[a+1]+dst,src,val+1,l*8+q);}
    }}cost.swap(ncost);
   }
   if(cost[goal]>=9999)continue;vector<array<int,4>>ops;int s=goal;
   for(int t=R;t>begin;t--){int src=prev[t*N+s],code=action[t*N+s],l=code/8,q=code%8;int a=int(upper_bound(off.begin(),off.end(),s)-off.begin())-1,pa=int(upper_bound(off.begin(),off.end(),src)-off.begin())-1;
    if(q<7)ops.push_back({t-1,pa==0?1:2,cells[q],-1});for(auto it=layers[l].rbegin();it!=layers[l].rend();++it){auto[u,v]=edges[*it];ops.push_back({t-1,0,cells[u],cells[v]});}s=src;
   }reverse(ops.begin(),ops.end());if(!first)cout<<",";first=false;cout<<"{\"family\":"<<family<<",\"mode\":"<<mode<<",\"R\":"<<R<<",\"cost\":"<<cost[goal]<<",\"pivots\":[";bool f=true;for(int q=0;q<7;q++)if(piv>>q&1){if(!f)cout<<",";f=false;cout<<cells[q];}cout<<"],\"mbops\":[";f=true;for(auto op:ops){if(!f)cout<<",";f=false;cout<<"["<<op[0]<<","<<op[1]<<","<<op[2]<<","<<op[3]<<"]";}cout<<"]}";
  }cerr<<"family "<<family<<" mode "<<mode<<" R"<<R<<" complete\n";
 }cout<<"]\n";
}
