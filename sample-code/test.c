#include <iostream>

using namespace std;

/*d11*/ //PRQA S 3138 EOF
/*d12*/ //PRQA S 3402 EOF


class A
{
public:
	A(){
		d=0;
		b[0]=b[1]=b[2]=b[3]=b[4]=b[5]=b[6]=b[7]=b[8]=b[9]=1;
	}
	void al();//finish!!
	void ac();//finish!!
	void ap();//finish!!
	void def();//finish!!
	void def2();//finish!!

	friend void ini(A &,int);//finish!!
	void give(int,int);//finish!!

	int b[10];
	int d;
	int l,c;
};

A a[10][10];

void ini(A & a,int t)
{
	a.d=t;
	a.b[1]=a.b[2]=a.b[3]=a.b[4]=a.b[5]=a.b[6]=a.b[7]=a.b[8]=a.b[9]=0;
	a.b[t]=1;
}

void A::def()
{
	int i;
	if(b[1]+b[2]+b[3]+b[4]+b[5]+b[6]+b[7]+b[8]+b[9]==1){
		for(i=1;i<=9;i++)
			if(b[i]==1)
				break;
		d=i;
		b[1]=b[2]=b[3]=b[4]=b[5]=b[6]=b[7]=b[8]=b[9]=0;	
		b[i]=1;
	}		
}

void A::give(int i,int j)
{
	l=i;
	c=j;
}

void A::al()
{
	int i;
	for(i=1;i<c;i++)
		if(a[l][i].d!=0)
			b[a[l][i].d]=0;
	for(i=c+1;i<=9;i++)
		if(a[l][i].d!=0)
			b[a[l][i].d]=0;
}

void A::ac()
{
	int i;
	for(i=1;i<l;i++)
		if(a[i][c].d!=0)
			b[a[i][c].d]=0;
	for(i=c+1;i<=9;i++)
		if(a[i][c].d!=0)
			b[a[i][c].d]=0;
}

void A::ap()
{
	int i,j;
	int m=l/3,n=c/3;
	if(l==3||l==6||l==9)
		m=m-1;
	if(c==3||c==6||c==9)
		n=n-1;
	for(j=m*3+1;j<=m*3+3;j++)
		for(i=n*3+1;i<=n*3+3;i++)
			if(a[j][i].d!=0)
				b[a[j][i].d]=0;	
}

void A::def2()
{
	int i;
	int m=l/3,n=c/3;
	if(d==0)
		for(i=1;i<=9;i++)
			if(b[i]!=0)
				if(a[l][1].b[i]+a[l][2].b[i]+a[l][3].b[i]+a[l][4].b[i]+a[l][5].b[i]+a[l][6].b[i]+a[l][7].b[i]+a[l][8].b[i]+a[l][9].b[i]==1){
					d=i;
				   b[1]=b[2]=b[3]=b[4]=b[5]=b[6]=b[7]=b[8]=b[9]=0;	
				   b[i]=1;
					 
				}

	if(d==0)
		for(i=1;i<=9;i++)
			if(b[i]!=0)
				if(a[1][c].b[i]+a[2][c].b[i]+a[3][c].b[i]+a[4][c].b[i]+a[5][c].b[i]+a[6][c].b[i]+a[7][c].b[i]+a[8][c].b[i]+a[9][c].b[i]==1){
					d=i;
					b[1]=b[2]=b[3]=b[4]=b[5]=b[6]=b[7]=b[8]=b[9]=0;	
					b[i]=1;
				
				}
						
	if(d==0){
		if(b[i]!=0)
		if(l==3||l==6||l==9)
			m=m-1;
		if(c==3||c==6||c==9)
			n=n-1;
		if(a[m*3+1][n*3+1].b[i]+a[m*3+1][n*3+2].b[i]+a[m*3+1][n*3+3].b[i]+a[m*3+2][n*3+1].b[i]+a[m*3+2][n*3+2].b[i]+a[m*3+2][n*3+3].b[i]+a[m*3+3][n*3+1].b[i]+a[m*3+3][n*3+2].b[i]+a[m*3+3][n*3+3].b[i]==1){
			d=i;
			b[1]=b[2]=b[3]=b[4]=b[5]=b[6]=b[7]=b[8]=b[9]=0;	
			b[i]=1;
		
		}
	}
}



int main()
{
	int i,j,k;
	
	ini(a[1][2],1);ini(a[1][4],6);ini(a[1][7],7);
	ini(a[2][1],2);ini(a[2][3],8);ini(a[2][6],3);ini(a[2][8],5);
	ini(a[3][2],5);ini(a[3][5],1);ini(a[3][9],4);
	ini(a[4][1],1);ini(a[4][6],4);
	ini(a[5][3],5);ini(a[5][7],6);
	ini(a[6][2],8);ini(a[6][4],3);ini(a[6][6],2);
	ini(a[7][1],9);ini(a[7][5],5);ini(a[7][8],4);
	ini(a[8][2],7);ini(a[8][7],1);ini(a[8][9],2);
	ini(a[9][3],6);ini(a[9][8],3);
	
   //input!!!!!!!!!!!!!!!!!!!!

	for(i=1;i<=9;i++)
		for(j=1;j<=9;j++)
			a[i][j].give(i,j);           //give xiabiao
		for(k=1;k<=30;k++){
	for(i=1;i<=9;i++)
		for(j=1;j<=9;j++)
			if(a[i][j].d==0){
				a[i][j].al();                // saomiao
				a[i][j].ac();
				a[i][j].ap();
			} 
	
	for(i=1;i<=9;i++)
		for(j=1;j<=9;j++)                   //dingyi
			a[i][j].def();

	for(i=1;i<=9;i++)
		for(j=1;j<=9;j++)                 
			a[i][j].def2();
		}

	for(i=1;i<=9;i++){
		cout<<endl;
		for(j=1;j<=9;j++)
			cout<<a[i][j].d<<" ";             //print chu lai
	}

    return 0;
}
