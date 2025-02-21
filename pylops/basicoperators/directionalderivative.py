__all__ = [
    "FirstDirectionalDerivative",
    "SecondDirectionalDerivative",
]

from pylops import LinearOperator
from pylops.basicoperators import Diagonal, Gradient, Sum
from pylops.utils.typing import DTypeLike, InputDimsLike, NDArray


def FirstDirectionalDerivative(
    dims: InputDimsLike,
    v: NDArray,
    sampling: int = 1,
    edge: bool = False,
    kind: str = "centered",
    dtype: DTypeLike = "float64",
) -> LinearOperator:
    r"""First Directional derivative.

    Apply a directional derivative operator to a multi-dimensional array
    along either a single common axis or different axes for each
    point of the array.

    .. note:: At least 2 dimensions are required, consider using
      :py:func:`pylops.FirstDerivative` for 1d arrays.

    Parameters
    ----------
    dims : :obj:`tuple`
        Number of samples for each dimension.
    v : :obj:`np.ndarray`, optional
        Single direction (array of size :math:`n_\text{dims}`) or group of directions
        (array of size :math:`[n_\text{dims} \times n_{d_0} \times ... \times n_{d_{n_\text{dims}}}]`)
    sampling : :obj:`tuple`, optional
        Sampling steps for each direction.
    edge : :obj:`bool`, optional
        Use reduced order derivative at edges (``True``) or
        ignore them (``False``).
    kind : :obj:`str`, optional
        Derivative kind (``forward``, ``centered``, or ``backward``).
    dtype : :obj:`str`, optional
        Type of elements in input array.

    Returns
    -------
    ddop : :obj:`pylops.LinearOperator`
        First directional derivative linear operator

    Notes
    -----
    The FirstDirectionalDerivative applies a first-order derivative
    to a multi-dimensional array along the direction defined by the unitary
    vector :math:`\mathbf{v}`:

    .. math::
        df_\mathbf{v} =
            \nabla f \mathbf{v}

    or along the directions defined by the unitary vectors
    :math:`\mathbf{v}(x, y)`:

    .. math::
        df_\mathbf{v}(x,y) =
            \nabla f(x,y) \mathbf{v}(x,y)

    where we have here considered the 2-dimensional case.

    This operator can be easily implemented as the concatenation of the
    :py:class:`pylops.Gradient` operator and the :py:class:`pylops.Diagonal`
    operator with :math:`\mathbf{v}` along the main diagonal.

    """
    Gop = Gradient(dims, sampling=sampling, edge=edge, kind=kind, dtype=dtype)
    if v.ndim == 1:
        Dop = Diagonal(v, dims=[len(dims)] + list(dims), axis=0, dtype=dtype)
    else:
        Dop = Diagonal(v.ravel(), dtype=dtype)
    Sop = Sum(dims=[len(dims)] + list(dims), axis=0, dtype=dtype)
    ddop = LinearOperator(Sop * Dop * Gop)
    ddop.dims = ddop.dimsd = dims
    ddop.sampling = sampling
    return ddop


def SecondDirectionalDerivative(
    dims: InputDimsLike,
    v: NDArray,
    sampling: int = 1,
    edge: bool = False,
    dtype: DTypeLike = "float64",
) -> LinearOperator:
    r"""Second Directional derivative.

    Apply a second directional derivative operator to a multi-dimensional array
    along either a single common axis or different axes for each
    point of the array.

    .. note:: At least 2 dimensions are required, consider using
      :py:func:`pylops.SecondDerivative` for 1d arrays.

    Parameters
    ----------
    dims : :obj:`tuple`
        Number of samples for each dimension.
    v : :obj:`np.ndarray`, optional
        Single direction (array of size :math:`n_\text{dims}`) or group of directions
        (array of size :math:`[n_\text{dims} \times n_{d_0} \times ... \times n_{d_{n_\text{dims}}}]`)
    sampling : :obj:`tuple`, optional
        Sampling steps for each direction.
    edge : :obj:`bool`, optional
        Use reduced order derivative at edges (``True``) or
        ignore them (``False``).
    dtype : :obj:`str`, optional
        Type of elements in input array.

    Returns
    -------
    ddop : :obj:`pylops.LinearOperator`
        Second directional derivative linear operator

    Notes
    -----
    The SecondDirectionalDerivative applies a second-order derivative
    to a multi-dimensional array along the direction defined by the unitary
    vector :math:`\mathbf{v}`:

    .. math::
        d^2f_\mathbf{v} =
            - D_\mathbf{v}^T [D_\mathbf{v} f]

    where :math:`D_\mathbf{v}` is the first-order directional derivative
    implemented by :func:`pylops.SecondDirectionalDerivative`.

    This operator is sometimes also referred to as directional Laplacian
    in the literature.
    """
    Dop = FirstDirectionalDerivative(dims, v, sampling=sampling, edge=edge, dtype=dtype)
    ddop = LinearOperator(-Dop.H * Dop)
    ddop.dims = ddop.dimsd = dims
    ddop.sampling = sampling
    return ddop
