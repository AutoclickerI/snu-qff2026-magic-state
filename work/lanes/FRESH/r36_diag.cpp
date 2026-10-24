#include <iostream>
#include <vector>
#include <map>
#include <string>
using namespace std;
struct Ins{int kind,g;vector<int>qs;};
int main(){int n,L;cin>>n>>L;vector<Ins>ins(L);for(auto &x:ins){int k;cin>>x.kind>>x.g>>k;x.qs.resize(k);for(int &q:x.qs)cin>>q;}
 map<pair<int,int>,int>badgate;int total=0,bad=0;cout<<"{\"failures\":[";bool first=true;
 for(int i=0;i<L;i++)if(ins[i].kind==1)for(int q:ins[i].qs)for(int axis=0;axis<2;axis++){
  total++;vector<int>A(n),v(n);vector<vector<int>>B(n,vector<int>(n));if(axis==0)v[q]=1;else A[q]=2;
  int failed=-1;for(int j=i+1;j<L;j++){auto&x=ins[j];if(x.kind!=0)continue;int a=x.qs[0],b=x.qs.size()>1?x.qs[1]:0;auto add=[&](int u,int val){A[u]=(A[u]+val)&3;};auto flip=[&](int u,int w){B[u][w]^=1;B[w][u]^=1;};
   switch(x.g){case 0:case 1:for(int l=0;l<n;l++)if(B[a][l])add(l,2);A[a]=(4-A[a])&3;break;
    case 2:break;case 3:case 4:if(v[a])add(a,2);break;case 5:if(v[a])add(b,2);if(v[b])add(a,2);break;
    case 6:{int at=A[b],bt=B[b][a];vector<int>snap=B[b];add(a,at+2*bt);if(at&1)flip(a,b);for(int l=0;l<n;l++)if(l!=a&&l!=b&&snap[l])flip(a,l);v[b]^=v[a];break;}
    case 7:{bool fail=A[a]&1;for(int t:B[a])fail|=t;if(fail){failed=j;break;}int z=A[a]==2;A[a]=v[a]?2:0;v[a]=z;break;}
    case 8:if(v[a])add(a,3);break;
    case 9:if(v[a]&&!v[b]){add(b,1);flip(a,b);}else if(!v[a]&&v[b]){add(a,1);flip(a,b);}else if(v[a]&&v[b]){add(a,3);add(b,3);}break;
    case 11:failed=j;break;
    default:cerr<<"unsupported "<<x.g;return 2;
   }if(failed>=0)break;
  }if(failed>=0){bad++;badgate[{failed,ins[failed].qs[0]}]++;if(!first)cout<<",";first=false;cout<<"["<<i<<","<<q<<","<<axis<<","<<failed<<","<<ins[failed].qs[0]<<"]";}
 }
 cout<<"],\"total_atoms\":"<<total<<",\"failed_atoms\":"<<bad<<",\"bad_gates\":[";first=true;for(auto &kv:badgate){if(!first)cout<<",";first=false;cout<<"["<<kv.first.first<<","<<kv.first.second<<","<<kv.second<<"]";}cout<<"]}\n";
}
