""" Project C

COMPLETE THIS FILE

Your names here:

"""
from .assignment6 import *

def flip (x):
    return np.transpose(x,axes= (1,0,2))

def dwt1d(x, h, g): # 1d and 1scale
    coarse = convolve(x, g)
    detail = convolve(x, h)
    z = np.concatenate((coarse[::2, :], detail[::2, :]), axis=0)
    return z

def dwt(x, J, h, g):
    if J == 0:
        return x
    n1, n2 = x.shape[:2]
    m1, m2 = (int(n1 / 2), int(n2 / 2))
    z = dwt1d(x, h, g)
    z = flip(dwt1d(flip(z), h, g))
    z[:m1, :m2] = dwt(z[:m1, :m2], J - 1, h, g)
    return z



def idwt(z, J, h, g): # 2d and multi-scale
    if J == 0:
        return z
    n1, n2 = z.shape[:2]
    m1, m2 = (int(n1 / 2), int(n2 / 2))
    x = z.copy()
    x[:m1, :m2] = idwt(x[:m1, :m2], J - 1, h, g)
    x = flip(idwt1d(flip(x), h, g))
    x = idwt1d(x, h, g)
    return x

def idwt1d(z, h, g): # 1d and 1scale
    n1 = z.shape[0]
    m1 = int(n1 / 2)
    coarse, detail = np.zeros(z.shape), np.zeros(z.shape)
    coarse[::2, :], detail[::2, :] = z[:m1, :], z[m1:, :]
    x = convolve(coarse, g[::-1]) + convolve(detail, h[::-1])
    return x
    

def shift(x, k, l, boundary):
    n1,n2 = x.shape[:2]
    xshifted = np.zeros(x.shape)
    if boundary is 'periodical':
        irange = np.mod(np.arange(n1) + k, n1)
        jrange = np.mod(np.arange(n2) + l, n2)
        xshifted = x[irange, :][:, jrange]
        
    if boundary is 'extension':
        irange = np.concatenate((np.zeros(max(-k,0), dtype = np.int32 ),np.arange(max(k,0), n1-max(-k,0)),
                                 (n1 - 1)* np.ones(max(k,0), dtype = np.int32)))
        jrange = np.concatenate((np.zeros(max(-l,0), dtype = np.int32),
                                 np.arange(max(l,0), n2-max(-l,0)),
                                 (n2 - 1)* np.ones(max(l,0), dtype = np.int32)))
        return x[irange, :][:, jrange]
    
    if boundary is 'mirror':
        irange = np.concatenate((np.arange(max(-k,0), 0, -1),np.arange(max(k,0), n1-max(-k,0)),
                                 (n1 - 1) - np.arange(0,max(k,0))))
        jrange = np.concatenate((np.arange(max(-l,0), 0, -1),
                                 np.arange(max(l,0), n2-max(-l,0)),
                                 (n2 - 1) - np.arange(0,max(l,0))))
        return x[irange, :][:, jrange]
    
    if boundary is 'zero-padding':
        if k < 0 :
            xshifted = np.roll(x,-k,axis = 0)
            xshifted[0:-k,:,:] = 0
        elif k>=0:
            xshifted = np.roll(x,-k, axis = 0)
            xshifted[n1-k:n1,:,:] = 0
        if l>=0:
            xshifted = np.roll(xshifted, -l, axis = 1)
            xshifted[:,n2-l:n2,:] = 0
        elif l<0:
            xshifted = np.roll(xshifted, -l, axis = 1)
            xshifted[:,0:-l,:] = 0
    return xshifted 

def convolve(x, nu, boundary='periodical', seperable='None'):
    xconv = np.zeros(x.shape)
    if seperable == 'None':
        s1 = int((nu.shape[0] - 1) / 2)
        s2 = int((nu.shape[1] - 1) / 2)
        for k in range(-s1, s1+1):
            for l in range(-s2, s2+1):
                xconv += nu[k+s1,l+s2]*shift(x,-k,-l,boundary )       
    elif seperable == 'product':
        xtemp = np.zeros(x.shape)
        s1 = int((nu[0].shape[0] - 1) / 2)
        s2 = int((nu[1].shape[1] - 1) / 2)
        for l in range(-s2, s2+1):
            xtemp += nu[1][0,l+s2]*shift(x,0,-l,boundary )
        for k in range(-s1, s1+1):
            xconv += nu[0][k+s1,0]*shift(xtemp,-k,0,boundary )
    elif seperable == 'sum':
        s1 = int((nu[0].shape[0] - 1) / 2)
        s2 = int((nu[1].shape[1] - 1) / 2)
        for k in range(-s1, s1+1):
            xconv += nu[0][k+s1,0]*shift(x,-k,0,boundary )
        for l in range(-s2, s2+1):
            xconv += nu[1][0,l+s2]*shift(x,0,-l,boundary )
    return xconv


class DWT:
    def __init__(self, shape, J, name):
        self.name = 'db2'
        self.J = J
        self.shape=shape
        h,g = wavelet('db2')
     
    def __call__(self, x):
        h,g = wavelet(self.name)
        x= dtw_crop(x,self.J)
        z_dwt= dwt(x,self.J,h,g)
        return z_dwt
    
    def invert(self,x):
        h,g = wavelet(self.name)
        x= dtw_crop(x,self.J)
        z_idwt = idwt(x,self.J,h,g)
        return z_idwt
    
    def power(self):
        n1,n2= self.shape[:2]
        J= self.J
        return dwt_power(n1, n2, self.J, ndim=len(self.shape))
        

    def adjoint(self, x):
        pass

    def gram(self, x):
        pass

    def gram_resolvent(self, x, tau):
        pass
    
    def wavelet(name, d=2):
    
        if name in ('haar', 'db1'):
            h = np.array([-1, 1])
        if name is 'db2':
            h = np.array([1, np.sqrt(3), -(3 + 2 * np.sqrt(3)), 2 + np.sqrt(3)])
        if name is 'db4':
            h = np.array(
            [-0.230377813308855230, +0.714846570552541500, -0.630880767929590400,
             -0.027983769416983850, +0.187034811718881140, +0.030841381835986965,
             -0.032883011666982945, -0.010597401784997278])
        if name is 'db8':
            h = np.array(
            [-0.0544158422, +0.3128715909, -0.6756307363, +0.5853546837,
             +0.0158291053, -0.2840155430, -0.0004724846, +0.1287474266,
             +0.0173693010, -0.0440882539, -0.0139810279, +0.0087460940,
             +0.0048703530, -0.0003917404, -0.0006754494, -0.0001174768])
        if name is 'sym4':
            h = np.array(
            [-0.03222310060404270, -0.012603967262037833, +0.09921954357684722,
             +0.29785779560527736, -0.803738751805916100, +0.49761866763201545,
             +0.02963552764599851, -0.075765714789273330])
        if name is 'coif4':
            h = np.array(
            [-0.00089231366858231460, -0.00162949201260173260, +0.00734616632764209350,
             +0.01606894396477634800, -0.02668230015605307200, -0.08126669968087875000,
             +0.05607731331675481000, +0.41530840703043026000, -0.78223893092049900000,
             +0.43438605649146850000, +0.06662747426342504000, -0.09622044203398798000,
             -0.03933442712333749000, +0.02508226184486409700, +0.01521173152794625900,
             -0.00565828668661072000, -0.00375143615727845700, +0.00126656192929894450,
             +0.00058902075624433830, -0.00025997455248771324, -6.2339034461007130e-05,
             +3.1229875865345646e-05, +3.2596802368833675e-06, -1.7849850030882614e-06])
        h = h / np.sqrt(np.sum(h**2))
        g = (-1)**(1 + np.arange(h.shape[0])) * h[::-1]
        h = np.concatenate((h, np.array([0.])))
        g = np.concatenate((g, np.array([0.])))
        h = h.reshape(-1, *[1] * (d - 1))
        g = g.reshape(-1, *[1] * (d - 1))
        return h, g
    
    def dtw_crop(x, J):
        n1, n2 = x.shape[:2]
        r1 = np.mod(n1, 2**J)
        r2 = np.mod(n2, 2**J)
        if r1 > 0:
            x = x[int(r1/2):-(r1-int(r1/2)), :]
        if r2 > 0:
            x = x[:, int(r2/2):-(r2-int(r2/2))]
        return x

def softthresh(z, t):
    new_z = (z - np.sign(z-t) * t) * np.maximum(np.abs(z)-t,0).astype(bool)
    #new_z = (z-t)*((z-t)>0)*(np.abs(z)>np.abs(t))+(z+t)*(z+t<0)
    
    return new_z

def softthresh_denoise(y, sig, W, alpha):
    n1,n2 = y.shape[:2]
    J=3
    h,g= wavelet('db2')
    #p= dwt_power(n1,n2,J=3,ndim=3)
    p=W.power()
    lamda=np.zeros(p.shape)
    tau=np.zeros(p.shape)
    lamda = alpha*p
    tau= (np.sqrt(2)*(sig**2))/lamda
    
    z=dtw_crop(y,J)
    z= dwt(y,J,h,g)
    z_denoise= softthresh(z,tau)
    denoise = idwt(z_denoise,J,h,g)
    return denoise


def dwt_power(n1, n2, J, ndim=3):

    if J == 0:
        return np.ones((n1, n2, *[1] * (ndim - 2)))
    m1, m2 = int(n1/2), int(n2/2)
    c = 2 * dwt_power(m1, m2, J - 1, ndim=ndim)
    de = np.ones((m1, m2, *[1] * (ndim - 2)))
    p = np.concatenate((np.concatenate((c, de), axis=0),
                        np.concatenate((de, de), axis=0)), axis=1)
    return p


# PSNR from assignment 4 for noise dB calculation

def psnr(x,x0):
    #import math
    
    # if something is a bit over 1 or less than 0
    test_nlm = np.round(x)

    # used any for faster checking
    if not ((test_nlm>1).any() or (test_nlm<0).any()):
        Rsquared = 1
    elif not ((test_nlm>255).any() or (test_nlm<0).any()):
        Rsquared = 255
    else:
        raise TypeError('not an image')
        
    n = x.size
    return 10*np.log10((n*Rsquared) / l2normsquared(x-x0))

def l2normsquared(z):
    if len(z.shape)==3:
        temp = (z**2).mean(axis=2)
    else:
        temp = z**2
        
    return np.sum(temp)




