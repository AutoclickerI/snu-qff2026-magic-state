#include <array>
#include <algorithm>
#include <bit>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>
using namespace std;
using S=array<unsigned,4>;
struct Hash{size_t operator()(const S&s)const{size_t h=0;for(auto x:s)h=h*137+x;return h;}};
S canon(S s){for(int i=0;i<4;i++){int j=i;for(int t=i+1;t<4;t++)if(countr_zero(s[t])<countr_zero(s[j]))j=t;swap(s[i],s[j]);unsigned bit=s[i]&-s[i];for(int t=0;t<4;t++)if(t!=i&&(s[t]&bit))s[t]^=s[i];}return s;}
int main(){
 vector<int> cells={1,14,8,9,2,16,15};vector<pair<int,int>> edges;vector<unsigned> touch;
 for(int i=0;i<7;i++)for(int j=0;j<7;j++)if(abs(cells[i]/6-cells[j]/6)+abs(cells[i]%6-cells[j]%6)==1){edges.push_back({i,j});touch.push_back((1u<<i)|(1u<<j));}
 auto trans=[&](S s,int e){auto[c,t]=edges[e];for(auto&x:s)if(x>>c&1)x^=1u<<t;return canon(s);};
 S target=canon({0b1010101,0b1100110,0b1111000,0b0000111});vector<S> states={target};unordered_map<S,int,Hash> ids;ids[target]=0;vector<vector<int>>adj;
 for(size_t i=0;i<states.size();i++){vector<int> row;for(int e=0;e<(int)edges.size();e++){S s=trans(states[i],e);if(!ids.count(s)){ids[s]=states.size();states.push_back(s);}row.push_back(ids[s]);}adj.push_back(row);}
 vector<vector<int>> layers(1);vector<unsigned> masks(1,0);vector<int> path;
 function<void(int,unsigned)> gen=[&](int k,unsigned used){for(int e=k;e<(int)edges.size();e++)if(!(used&touch[e])){path.push_back(e);layers.push_back(path);masks.push_back(used|touch[e]);gen(e+1,used|touch[e]);path.pop_back();}};gen(0,0);
 int N=states.size(),M=layers.size();vector<vector<int>>next(N,vector<int>(M));for(int s=0;s<N;s++)for(int l=0;l<M;l++){int x=s;for(int e:layers[l])x=adj[x][e];next[s][l]=x;}
 cerr<<N<<" states "<<M<<" layers\n";
 int jobs;cin>>jobs;cout<<"[";bool first=true;
 for(int job=0;job<jobs;job++){
  int mode,R;cin>>mode>>R;array<int,7>rx,rz;for(auto&x:rx)cin>>x;for(auto&x:rz)cin>>x;
  int mc,mt,helper,bs,bv;cin>>mc>>mt>>helper>>bs>>bv;int bf=bv+2;vector<int>remote(N);
  if(mc>=0)for(int s=0;s<N;s++){S ns=states[s];for(auto&x:ns)if(x>>mc&1)x^=1u<<mt;remote[s]=ids.at(canon(ns));}
  for(unsigned piv=0;piv<128;piv++)if(popcount(piv)==4){S start{};int k=0;array<int,7>ready;for(int q=0;q<7;q++){if(piv>>q&1)start[k++]=1u<<q;ready[q]=(piv>>q&1)?rx[q]:rz[q];}int init=ids.at(canon(start));int begin=*min_element(ready.begin(),ready.end());
   if(mc>=0&&(ready[mc]>bs||ready[mt]>bv))continue;
   vector<int>cost(N,999),ncost(N),prev((R+1)*N,-1),pl((R+1)*N,-1);cost[init]=0;
   for(int t=begin;t<R;t++){
    fill(ncost.begin(),ncost.end(),999);unsigned avail=0;for(int q=0;q<7;q++)if(ready[q]<=t)avail|=1u<<q;
    if(mc>=0){if(t>=bs&&t<=bf)avail&=~(1u<<mc);if(t>=bv&&t<=bf)avail&=~(1u<<mt);}
    vector<int>ls;for(int l=0;l<M;l++)if((masks[l]&avail)==masks[l])ls.push_back(l);
    for(int s=0;s<N;s++)if(cost[s]<999)for(int l:ls){int ns=next[s][l],c=cost[s]+layers[l].size();if(mc>=0&&t==bf){ns=remote[ns];c+=4;}if(c<ncost[ns]){ncost[ns]=c;prev[(t+1)*N+ns]=s;pl[(t+1)*N+ns]=l;}}
    cost.swap(ncost);
   }
   if(cost[0]>=999)continue;vector<pair<int,int>>sol;int s=0;for(int t=R;t>begin;t--){int l=pl[t*N+s];if(l<0){cerr<<"bad backtrack\n";return 2;}if(l)sol.push_back({t-1,l});s=prev[t*N+s];}reverse(sol.begin(),sol.end());
   if(!first)cout<<",";first=false;cout<<"{\"mode\":"<<mode<<",\"R\":"<<R<<",\"cx\":"<<cost[0]<<",\"pivots\":[";bool f=true;for(int q=0;q<7;q++)if(piv>>q&1){if(!f)cout<<",";f=false;cout<<cells[q];}cout<<"],\"ops\":[";f=true;for(auto[t,l]:sol)for(int e:layers[l]){if(!f)cout<<",";f=false;auto[a,b]=edges[e];cout<<"["<<t<<","<<cells[a]<<","<<cells[b]<<"]";}cout<<"]";
   if(mc>=0)cout<<",\"bus\":[["<<bs<<","<<cells[mc]<<","<<helper<<"],["<<bv<<","<<helper<<","<<cells[mt]<<"],["<<bv+1<<","<<cells[mc]<<","<<helper<<"],["<<bf<<","<<helper<<","<<cells[mt]<<"]]";
   cout<<"}";
  }
  cerr<<"job "<<mode<<" R"<<R<<" complete\n";
 }
 cout<<"]\n";
}
