#include <bits/stdc++.h>
using namespace std;
int canonical(array<int,3>s){for(int i=0;i<3;i++){int j=i;for(int k=i+1;k<3;k++)if(__builtin_ctz(s[k])<__builtin_ctz(s[j]))j=k;swap(s[i],s[j]);int bit=s[i]&-s[i];for(int k=0;k<3;k++)if(k!=i&&(s[k]&bit))s[k]^=s[i];}return s[0]|s[1]<<7|s[2]<<14;}
int change(int key,int u,int v){array<int,3>s;for(int i=0;i<3;i++){s[i]=(key>>(7*i))&127;if((s[i]>>u)&1)s[i]^=1<<v;}return canonical(s);}
int main(int argc,char**argv){int ns,nt;cin>>ns>>nt;vector<int>targets(nt);for(auto&v:targets)cin>>v;
 vector<int>states;unordered_map<int,int>ids;auto add=[&](int x){if(!ids.count(x)){ids[x]=states.size();states.push_back(x);}};
 vector<int>initial;for(int a=0;a<7;a++)for(int b=a+1;b<7;b++)for(int c=b+1;c<7;c++){int k=canonical({1<<a,1<<b,1<<c});add(k);initial.push_back(ids[k]);}
 vector<array<int,49>>trans;
 for(int i=0;i<(int)states.size();i++){int x=states[i];array<int,49>row{};for(int u=0;u<7;u++)for(int v=0;v<7;v++)if(u!=v){int y=change(x,u,v);add(y);row[u*7+v]=ids[y];}trans.push_back(row);}
 assert(states.size()==11811);cerr<<"states "<<states.size()<<"\n";cout<<"[";
 ofstream cert; if(argc>1){cert.open(argv[1],ios::binary);int n=states.size();cert.write((char*)&ns,4);cert.write((char*)&n,4);cert.write((char*)states.data(),4*n);}
 for(int g=0;g<ns;g++){int ne;cin>>ne;vector<pair<int,int>>es(ne);for(auto&[u,v]:es)cin>>u>>v;
 vector<vector<int>>layers;vector<int>tmp;
 function<void(int,int)>enumerate=[&](int at,int used){for(int e=at;e<ne;e++){auto[u,v]=es[e];int touch=(1<<u)|(1<<v);if(used&touch)continue;tmp.push_back(e);layers.push_back(tmp);enumerate(e+1,used|touch);tmp.pop_back();}};enumerate(0,0);
 vector<int>d(states.size(),100000000),prev(states.size(),-1),pe(states.size(),-1);priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>>queue;
 for(int i:initial)d[i]=0,queue.push({0,i});
 while(!queue.empty()){auto[cost,x]=queue.top();queue.pop();if(cost!=d[x])continue;for(int li=0;li<(int)layers.size();li++){auto&layer=layers[li];int y=x;for(int e:layer){auto[u,v]=es[e];y=trans[y][u*7+v];}int nd=cost+1000+layer.size();if(nd<d[y]){d[y]=nd;prev[y]=x;pe[y]=li;queue.push({nd,y});}}}
 if(argc>1)for(int x:d){unsigned char dd=x;cert.write((char*)&dd,1);}
 if(g)cout<<",";cout<<"[";
 for(int j=0;j<nt;j++){int x=ids.at(targets[j]);vector<int>lis;int dd=d[x];while(prev[x]>=0){lis.push_back(pe[x]);x=prev[x];}reverse(lis.begin(),lis.end());vector<pair<int,int>>path;for(int li:lis)for(int e:layers[li])path.push_back(es[e]);if(j)cout<<",";cout<<"{\"cx\":"<<dd%1000<<",\"depth\":"<<dd/1000<<",\"pivots\":[";for(int i=0;i<3;i++){if(i)cout<<",";cout<<__builtin_ctz((states[x]>>(7*i))&127);}cout<<"],\"ops\":[";for(int i=0;i<(int)path.size();i++){if(i)cout<<",";cout<<"["<<path[i].first<<","<<path[i].second<<"]";}cout<<"]}";}
 cout<<"]";
 }cout<<"]\n";
}
