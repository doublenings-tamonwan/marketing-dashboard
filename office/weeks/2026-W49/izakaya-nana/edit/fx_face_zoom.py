import numpy as np
from PIL import Image, ImageFilter
def ell_mask(w,h,c,rx,ry,blur=60):
    y,x=np.mgrid[0:h,0:w]; d=((x-c[0])/rx)**2+((y-c[1])/ry)**2
    m=np.clip(1.2-d,0,1); return np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(blur)))/255.
def skin(a):  # a float 0..1 rgb -> skin-ness mask
    r,g,b=a[...,0],a[...,1],a[...,2]; mx=a.max(-1); mn=a.min(-1)
    s=(mx-mn)/(mx+1e-6); m=((r>g)&(g>=b*0.85)&(s>0.06)&(s<0.6)&(mx>0.25)).astype(float)
    return np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(6)))/255.
def warm_face(img,c,rx,ry,amt=1.0):
    a=np.asarray(img.convert('RGB')).astype(float)/255; h,w,_=a.shape
    m=(ell_mask(w,h,c,rx,ry)*skin(a))[...,None]*amt
    b=a.copy(); b=np.clip(b**0.88,0,1)  # lift midtones
    b[...,0]*=1.06; b[...,1]*=1.015; b[...,2]*=0.93
    gray=b.mean(-1,keepdims=True); b=gray+(b-gray)*1.22  # a bit more colour
    o=a*(1-m)+np.clip(b,0,1)*m
    return Image.fromarray((o*255).astype('uint8'))
def big_head(img,c,R,k):
    a=np.asarray(img.convert('RGB')); h,w,_=a.shape
    y,x=np.mgrid[0:h,0:w].astype(float); dx,dy=x-c[0],y-c[1]; r=np.hypot(dx,dy)
    t=np.clip(r/R,0,1); f=1-(1-1/k)*(1-t**2)**2
    sx=np.clip(c[0]+dx*f,0,w-1); sy=np.clip(c[1]+dy*f,0,h-1)
    x0,y0=np.floor(sx).astype(int),np.floor(sy).astype(int); x1,y1=np.minimum(x0+1,w-1),np.minimum(y0+1,h-1)
    fx,fy=(sx-x0)[...,None],(sy-y0)[...,None]; A=a.astype(float)
    o=A[y0,x0]*(1-fx)*(1-fy)+A[y0,x1]*fx*(1-fy)+A[y1,x0]*(1-fx)*fy+A[y1,x1]*fx*fy
    return Image.fromarray(o.astype('uint8'))
def zoom(img,z,c):
    w,h=img.size; cw,ch=w/z,h/z; x=min(max(c[0]-cw/2,0),w-cw); y=min(max(c[1]-ch/2,0),h-ch)
    return img.crop((x,y,x+cw,y+ch)).resize((w,h),Image.LANCZOS)
