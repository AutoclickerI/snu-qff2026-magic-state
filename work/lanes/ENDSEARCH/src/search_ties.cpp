#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
using Layer=vector<pair<int,int>>;
ofstream ties;
int n,depth; vector<Layer> layers;vector<int> seq;vector<vector<int>> perms;
long long raw=0,canonical=0,measures=0,fullrank=0,scored=0,logicaltrials=0;
struct Resource {vector<int>x,z;int product;};vector<Resource> resources;
struct Fault {int x,z,w;};vector<Fault> faults;
struct Winner {double cost=1e30;string row;};map<string,vector<Winner>> best;
int parity(int a){return __builtin_parity((unsigned)a);}
vector<int> span(vector<int> b){vector<int>s{0};for(int v:b){auto old=s;for(int x:old)s.push_back(x^v);}sort(s.begin(),s.end());s.erase(unique(s.begin(),s.end()),s.end());return s;}
vector<int> basis(vector<int> v){int p[8]={};vector<int>b;for(int x:v){int y=x;for(int k=7;k>=0;k--)if(y>>k&1){if(p[k])y^=p[k];else{p[k]=y;b.push_back(x);break;}}}return b;}
void cx(int &x,int &z,int a,int b){if(x>>a&1)x^=1<<b;if(z>>b&1)z^=1<<a;}
pair<int,int> propagate(int x,int z,int after){for(int t=after+1;t<depth;t++)for(auto [a,b]:layers[seq[t]])cx(x,z,a,b);return {x,z};}
void makeres(){resources.clear();int a=n-1;set<vector<int>> subs;subs.insert({0});bool change=true;while(change){change=false;auto old=subs;for(auto s:old)for(int v=1;v<(1<<a);v++)if(!binary_search(s.begin(),s.end(),v)){auto q=s;for(int w:s)q.push_back(w^v);sort(q.begin(),q.end());if(subs.insert(q).second)change=true;}}
 for(auto s:subs){Resource r;for(int v:basis(s))r.x.push_back(v<<1);vector<int>orth;for(int v=0;v<(1<<a);v++){bool ok=true;for(int w:s)if(parity(v&w)){ok=false;break;}if(ok)orth.push_back(v);}for(int v:basis(orth))r.z.push_back(v<<1);r.product=0;int units=0;for(int j=0;j<a;j++)if(binary_search(s.begin(),s.end(),1<<j))units|=1<<j;if((1<<__builtin_popcount((unsigned)units))==(int)s.size())r.product=units;else r.product=-1;resources.push_back(r);}}
void makelayers(int mask,Layer cur){if(!mask){if(cur.size())layers.push_back(cur);return;}int a=__builtin_ctz((unsigned)mask);makelayers(mask^(1<<a),cur);for(int b=a+1;b<n;b++)if(mask>>b&1)for(int rev=0;rev<2;rev++){auto q=cur;q.push_back(rev?pair{b,a}:pair{a,b});sort(q.begin(),q.end());makelayers(mask^(1<<a)^(1<<b),q);}}
string sequence(const vector<int>&p){string s;for(int t:seq){Layer l;for(auto [a,b]:layers[t])l.push_back({p[a],p[b]});sort(l.begin(),l.end());for(auto [a,b]:l){s+=char('0'+a);s+=char('0'+b);}s+=';';}return s;}
bool canon(){vector<int>p(n);for(int j=0;j<n;j++)p[j]=j;string s=sequence(p);for(auto q:perms)if(sequence(q)<s)return false;return true;}
string jvec(vector<int>v){ostringstream o;o<<'[';for(int j=0;j<(int)v.size();j++)o<<(j?",":"")<<v[j];o<<']';return o.str();}
void examine(int outputmax){raw++;if(!canon())return;canonical++;int last[5];fill(last,last+n,-1);int edgemask=0;bool adj[5][5]={};int deg[5]={};for(int t=0;t<depth;t++)for(auto [a,b]:layers[seq[t]]){last[a]=last[b]=t;adj[a][b]=adj[b][a]=true;}
 int reach=1;for(int t=0;t<n;t++)for(int a=0;a<n;a++)if(reach>>a&1)for(int b=0;b<n;b++)if(adj[a][b])reach|=1<<b;if(reach!=(1<<n)-1)return;
 int edges=0;for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(adj[a][b])edges++,deg[a]++,deg[b]++;string graph=edges==n-1?"tree":edges==n&&*max_element(deg,deg+n)==2?"cycle":"hops";
 faults.clear();for(int t=0;t<depth;t++){int used=0;for(auto [a,b]:layers[seq[t]]){used|=(1<<a)|(1<<b);for(int pa=0;pa<4;pa++)for(int pb=0;pb<4;pb++)if(pa||pb){int x=((pa&1)<<a)|((pb&1)<<b),z=(((pa>>1)&1)<<a)|(((pb>>1)&1)<<b);auto q=propagate(x,z,t);faults.push_back({q.first,q.second,1});}}
 for(int q=0;q<n;q++)if(!(used>>q&1))for(int p=1;p<4;p++){auto v=propagate((p&1)<<q,((p>>1)&1)<<q,t);faults.push_back({v.first,v.second,5});}}
 auto ex=propagate(1,0,-1),ez=propagate(0,1,-1);
 // Transformed Choi stabilizer spans for all CSS logical resources.
 vector<pair<vector<int>,vector<int>>> spaces;
 for(int out=0;out<outputmax;out++){int modes=1;for(int q=0;q<n-1;q++)modes*=3;for(int m=0;m<modes;m++){int mx=0,mz=0,k=m;for(int q=0;q<n;q++)if(q!=out){int v=k%3;k/=3;if(v==1)mx|=1<<q;if(v==2)mz|=1<<q;}measures++;int measured=mx|mz;int rank=((ex.first&mz)||(ex.second&mx)?3:0)+((ez.first&mz)||(ez.second&mx)?3:0);if(rank!=6)continue;fullrank++;
 bool extra=false;for(int q=0;q<n;q++)if((measured>>q&1)&&last[q]==depth-1)extra=true;
 int partner=-1;for(auto[a,b]:layers[seq[depth-1]])if(a==out)partner=b;else if(b==out)partner=a;
 string terminal=!extra&&partner>=0&&!(measured>>partner&1)?"unmeasured":"idle";
 double rr[4]={};for(auto f:faults)if(!(f.x&mz)&&!(f.z&mx))rr[((f.x>>out)&1)|(((f.z>>out)&1)<<1)]+=f.w;
 if(extra)for(int p=1;p<4;p++)rr[p]+=5;
 double x=rr[1],y=rr[3],z=rr[2];double cost=21*(.5*(x+y)*(x+y)+z*z+2*y*z)/225;scored++;
 string prefix=to_string(n)+"/"+graph+"/"+terminal+"/"+(out?"handoff":"same");
 // Keep the three distinct leading coefficients per frontier category and
 // both self-checking/non-self-checking logical-resource contracts.
 bool candidate=false;for(int guard=0;guard<2;guard++)for(int prod=0;prod<2;prod++){auto key=prefix+"/"+to_string(guard)+"/"+to_string(prod);if(best[key].size()<3||cost<best[key].back().cost+1e-9)candidate=true;}if(!candidate)continue;
 if(spaces.empty())for(auto r:resources){auto xs=r.x,zs=r.z;xs.push_back(1|(1<<n));zs.push_back(1|(1<<n));for(int &x:xs){int z=0;for(int t:seq)for(auto[a,b]:layers[t])cx(x,z,a,b);}for(int &z:zs){int x=0;for(int t:seq)for(auto[a,b]:layers[t])cx(x,z,a,b);}spaces.push_back({span(xs),span(zs)});}
 for(int ri=0;ri<(int)resources.size();ri++){logicaltrials++;auto [xs,zs]=spaces[ri];int corr=(1<<out)|(1<<n),fx=-1,fz=-1;for(int v:xs)if((v&~mx)==corr){int f=v&mx;if(fz<0||__builtin_popcount((unsigned)f)<__builtin_popcount((unsigned)fz))fz=f;}if(fz<0)continue;for(int v:zs)if((v&~mz)==corr){int f=v&mz;if(fx<0||__builtin_popcount((unsigned)f)<__builtin_popcount((unsigned)fx))fx=f;}if(fx<0)continue;
 vector<int>dets;for(int v:xs)if(v&&!(v&~mx))dets.push_back(v);for(int v:zs)if(v&&!(v&~mz))dets.push_back(v);dets=basis(dets);
 int guard=1;vector<int>danger;for(int q=1;q<n;q++)for(int p=1;p<4;p++){auto f=propagate((p&1)<<q,((p>>1)&1)<<q,-1);int rec=(f.first&mz)|(f.second&mx);bool detected=false;for(int d:dets)if(parity(d&rec))detected=true;if(!detected){int ox=((f.first>>out)&1)^parity(fx&rec),oz=((f.second>>out)&1)^parity(fz&rec);if(ox||oz){guard=0;danger.push_back(q*4+p);}}}
 if(cost>26.7)continue;
 int prod=resources[ri].product>=0;string key=prefix+"/"+to_string(guard)+"/"+to_string(prod);auto &vv=best[key];
 ostringstream o;o.precision(17);o<<"{\"n\":"<<n<<",\"depth\":"<<depth<<",\"output\":"<<out<<",\"layers\":[";for(int t=0;t<depth;t++){if(t)o<<',';o<<'[';for(int j=0;j<(int)layers[seq[t]].size();j++){auto[a,b]=layers[seq[t]][j];if(j)o<<',';o<<'['<<a<<','<<b<<']';}o<<']';}o<<"],\"resource_x\":"<<jvec(resources[ri].x)<<",\"resource_z\":"<<jvec(resources[ri].z)<<",\"product_plus_mask\":"<<resources[ri].product<<",\"read_x\":"<<mx<<",\"read_z\":"<<mz<<",\"frame_x\":"<<fx<<",\"frame_z\":"<<fz<<",\"logical_detectors\":"<<jvec(dets)<<",\"logical_resource_guard\":"<<guard<<",\"dangerous_resource_paulis\":"<<jvec(danger)<<",\"graph\":\""<<graph<<"\",\"terminal\":\""<<terminal<<"\",\"rates_XYZ\":["<<x<<','<<y<<','<<z<<"],\"second_order_p2\":"<<cost<<",\"incoming_syndrome_rank\":6,\"first_order\":0,\"category\":\""<<key<<"\"}";
 ties<<o.str()<<'\n';
 }
 }}
}
int main(int argc,char**argv){n=stoi(argv[1]);ties.open("logs/ties_"+to_string(n)+".jsonl");int dmax=stoi(argv[2]);int outputmax=argc>3&&string(argv[3])=="handoff"?n:1;makelayers((1<<n)-1,{});sort(layers.begin(),layers.end());layers.erase(unique(layers.begin(),layers.end()),layers.end());vector<int>p(n);for(int j=0;j<n;j++)p[j]=j;do{perms.push_back(p);}while(next_permutation(p.begin()+1,p.end()));makeres();
 for(depth=2;depth<=dmax;depth++){seq.resize(depth);function<void(int)>go=[&](int t){if(t==depth){examine(outputmax);return;}for(int i=0;i<(int)layers.size();i++){seq[t]=i;if(t==0){vector<int>id(n);for(int j=0;j<n;j++)id[j]=j;auto original=layers[i];bool can=true;for(auto p:perms){Layer l;for(auto[a,b]:original)l.push_back({p[a],p[b]});sort(l.begin(),l.end());if(l<original){can=false;break;}}if(!can)continue;}go(t+1);}};go(0);cerr<<"n="<<n<<" depth="<<depth<<" canonical="<<canonical<<" measures="<<measures<<" scored="<<scored<<" logicaltrials="<<logicaltrials<<endl;}
 for(auto [key,v]:best)for(auto w:v)cout<<w.row<<'\n';cerr<<"COUNTS {\"n\":"<<n<<",\"max_depth\":"<<dmax<<",\"raw_after_first_layer_symmetry\":"<<raw<<",\"canonical\":"<<canonical<<",\"measurement_assignments\":"<<measures<<",\"full_rank\":"<<fullrank<<",\"scored\":"<<scored<<",\"logical_trials\":"<<logicaltrials<<",\"resources\":"<<resources.size()<<"}"<<endl;
}
