#include <bits/stdc++.h>
using namespace std;
int canonical(array<int,3>s){for(int i=0;i<3;i++){int j=i;for(int k=i+1;k<3;k++)if(__builtin_ctz(s[k])<__builtin_ctz(s[j]))j=k;swap(s[i],s[j]);int bit=s[i]&-s[i];for(int k=0;k<3;k++)if(k!=i&&(s[k]&bit))s[k]^=s[i];}return s[0]|s[1]<<8|s[2]<<16;}
int change(int key,int u,int v){array<int,3>s;for(int i=0;i<3;i++){s[i]=(key>>(8*i))&255;if((s[i]>>u)&1)s[i]^=1<<v;}return canonical(s);}
int main(){int n,ne,nt;cin>>n>>ne>>nt;vector<pair<int,int>>es(ne);for(auto&[u,v]:es)cin>>u>>v;vector<int>targets(nt);for(int&x:targets)cin>>x;
 vector<int>states,dist,prev,pe;unordered_map<int,int>ids;auto add=[&](int x,int dd,int pp,int ee){if(!ids.count(x)){ids[x]=states.size();states.push_back(x);dist.push_back(dd);prev.push_back(pp);pe.push_back(ee);}};
 for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)for(int c=b+1;c<n;c++)add(canonical({1<<a,1<<b,1<<c}),0,-1,-1);
 for(int i=0;i<(int)states.size();i++){int x=states[i];for(int e=0;e<ne;e++){auto[u,v]=es[e];add(change(x,u,v),dist[i]+1,i,e);}}
 cerr<<"states "<<states.size()<<"\n";cout<<"[";
 for(int j=0;j<nt;j++){if(j)cout<<",";if(!ids.count(targets[j])){cout<<"null";continue;}int x=ids.at(targets[j]);vector<pair<int,int>>path;int dd=dist[x];while(prev[x]>=0){path.push_back(es[pe[x]]);x=prev[x];}reverse(path.begin(),path.end());cout<<"{\"cx\":"<<dd<<",\"pivots\":[";for(int i=0;i<3;i++){if(i)cout<<",";cout<<__builtin_ctz((states[x]>>(8*i))&255);}cout<<"],\"ops\":[";for(int i=0;i<(int)path.size();i++){if(i)cout<<",";cout<<"["<<path[i].first<<","<<path[i].second<<"]";}cout<<"]}";}
 cout<<"]\n";
}
