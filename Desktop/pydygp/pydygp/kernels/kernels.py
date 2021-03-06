import numpy as np


class ParameterCollection:
    def __init__(self):
        pass

class KernelParameter:
    def __init__(self):
        pass

class Kernel:

    def __init__(self, kfunc, kpar, **kwargs):
        self.kfunc = kfunc  # Callable giving cov{Y(x1), Y(x2)}
        self.kpar = kpar    # additional arguments to kfunc

        try:
            self.dim = kwargs['dim']
            self.cov_method = kwargs['cov_method']
            self.par_grad = kwargs['par_grad']
        except:
            pass


    def cov(self, x1, x2=None, kpar=None):
        if kpar is None:
            if isinstance(self.kpar, KernelParameter):
                kpar = self.kpar.get_value()
            elif isinstance(self.kpar, ParameterCollection):
                kpar = self.kpar.value()
            else:
                kpar = self.kpar

        if not isinstance(x1, np.ndarray):
            x1 = np.asarray(x1)

        if not isinstance(x2, (float, list, np.ndarray)):
            if x2 is None:
                x2 = x1.copy()
            else:
                raise ValueError("Unrecognised input to kernel covariance function")

        # Optionally supplied cov method takes precedence
        try:
            return self.cov_method(x1, x2, kpar)
        except:
            T, S = np.meshgrid(x2, x1)
            return self.kfunc(S.ravel(), T.ravel(), kpar,
                              **kwargs).reshape(T.shape)


    def cov_par_grad(self, kpar, x1, x2=None, ind=-1):

        if not isinstance(x1, np.ndarray):
            x1 = np.asarray(x1)

        if not isinstance(x2, (float, list, np.ndarray)):
            if x2 is None:
                x2 = x1.copy()
            else:
                raise ValueError("Unrecognised input to kernel covariance function")

        try:
            return self.par_grad(x1, x2, kpar, ind)
        except:
            pass


    def __add__(self, other):
        if isinstance(other, Kernel):
            return AddKernel([self, other])
        elif isinstance(other, AddKernel):
            return AddKernel([self] + other.kernels)


    @classmethod
    def SquareExponKernel(cls, kpar=None, dim=1):
        if not isinstance(kpar, np.ndarray):
            if kpar is None:
                kpar = np.ones(dim+1)
        if dim >= 1:
            def cov_method(xx1, xx2, par):
                xs = [np.meshgrid(x2, x1) for x1, x2 in zip(xx1.T, xx2.T)]
                exp_arg = sum(p*(x[0]-x[1])**2 for (x, p) in zip(xs, par[1:]))
                return par[0]*np.exp(-exp_arg)

            def par_grad(xx1, xx2, par, ind=-1):
                if ind < 0:
                    cov = cov_method(xx1, xx2, par)
                    dkdp0 = cov_method(xx1, xx2, np.concatenate(([1.], par[1:])))
                    xs = [np.meshgrid(x2, x1) for x1, x2 in zip(xx1.T, xx2.T)]
                    dkdpi = [-(x[0]-x[1])**2*cov for x in xs]
                    return [dkdp0]+dkdpi
                elif ind == 0:
                    return cov_method(xx1, xx2, np.concatenate(([1.], par[1:])))
                else:
                    cov = cov_method(xx1, xx2, par)
                    x2, x1 = np.meshgrid(xx2[:, ind-1], xx1[:, ind-1])
                    return -(x2-x1)**2*cov
            
            return cls(None, kpar,
                       cov_method=cov_method,
                       dim=dim,
                       par_grad=par_grad)


    @classmethod
    def PeriodicKernel(cls, kpar=None):
        if not isinstance(kpar, np.ndarray):
            if kpar is None:
                kpar = np.ones(3)
            
        def cov_method(xx1, xx2, par):
            exp_arg = 2*np.sin(np.pi*np.abs(xx1.ravel()-xx2.ravel())/par[2])
            return par[0]**2*np.exp(-exp_arg/par[1]**2)

        return cls(None, kpar,
                   cov_method=cov_method,
                   dim=1)


class GradientKernel(Kernel):

    def __init__(self, kfunc, kpar, **kwargs):
        super(GradientKernel, self).__init__(kfunc, kpar, **kwargs)

    def cov(self,
            x1, x2=None, kpar=None,
            i=None, j=None, comp="x",
            **kwargs):

        if kpar is None:
            if isinstance(self.kpar, KernelParameter):
                kpar = self.kpar.get_value()
            elif isinstance(self.kpar, ParameterCollection):
                kpar = self.kpar.value()
            else:
                kpar = self.kpar

        if not isinstance(x1, np.ndarray):
            x1 = np.asarray(x1)

        if not isinstance(x2, (float, list, np.ndarray)):
            if x2 is None:
                x2 = x1.copy()
            else:
                raise ValueError("x2 input should be ... {}")

        # Optionally supplied cov method takes precedence
        try:

            if comp == 'dxdx' and i is None and j is None:

                # ToDo - ...
                #
                cov = np.row_stack((
                    np.column_stack((self.cov_method(x1, x2, kpar,
                                                     i=_i, j=_j,
                                                     comp=comp)
                                     for _j in range(self.dim)))
                    for _i in range(self.dim)))
                return cov
        except:
            pass


class AddKernel:
    def __init__(self, kernels):
        self.kernels = kernels


    def cov(self, x1, x2=None):

        if not isinstance(x1, np.ndarray):
            x1 = np.asarray(x1)

        if not isinstance(x2, (float, list, np.ndarray)):
            if x2 is None:
                x2 = x1.copy()
            else:
                raise ValueError("Unrecognised input to kernel covariance function")

        return sum(kernel.cov(x1, x2) for kernel in self.kernels)

    def __add__(self, other):
        if isinstance(other, Kernel):
            return AddKernel(self.kernels + [other])
        elif isinstance(other, AddKernel):
            return AddKernel(self.kernels + other.kernels)



