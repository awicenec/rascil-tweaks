# === RASCIL imports required for function overrides ====
# RASCIL needs to be installed as well in order for this
# to work.
import astropy.units as units
import astropy.wcs as wcs
import logging
import numpy
from astropy.coordinates import EarthLocation
from collections.abc import Sequence
from rascil.data_models.memory_data_models import (
    BlockVisibility,
    Configuration,
    Image,
)
from rascil.data_models.parameters import get_parameter
from rascil.data_models.polarisation import PolarisationFrame
from rascil.processing_components.fourier_transforms import ifft
from rascil.processing_components.fourier_transforms.fft_coordinates import coordinates
from rascil.processing_components.griddata.convolution_functions import \
    create_convolutionfunction_from_image
from rascil.processing_components.image.operations import (
    create_image_from_array,
)
from rascil.processing_components.simulation.configurations import (
    create_configuration_from_file,
)
from typing import Any

log = logging.getLogger("rascil-logger")


def griddataExtract(griddata: Sequence, index: int = 0) -> Any:
    return griddata[index]


def phasecentreExtract(vis) -> Any:
    return vis.phasecentre


def visExtract(vis: Sequence, index: int = 0) -> Any:
    return vis[index]


def polFrameExtract(vis) -> Any:
    return vis._polarisation_frame


def wcsExtract(im):
    return im.image_acc.wcs


def cfExtract(cf):
    return cf[1]


def create_MWA_configuration(
    filename: str = "MWAtiles.csv", **kwargs
) -> Configuration:
    """
    Create a configuration object for the MWA using the MWA tile positions from
    https://www.mwatelescope.org/images/documents/Merged%20MWA%20tile%20coordinates%20-%20AW%202018-06-21.xlsx
    """
    mwa_location = EarthLocation(
        lon="116:40:14.93", lat="-26:42:11.95", height=377
    )
    return create_configuration_from_file(
        filename, mwa_location, diameter=5 * numpy.sqrt(2)
    )


def polarisation_frame_from_names(names):
    """Derive polarisation_name from names

    :param names:
    :return:
    """
    if (
        isinstance(names, str)
        and names in PolarisationFrame.polarisation_frames
    ):
        return PolarisationFrame(names)
    elif isinstance(names, list):
        for frame in PolarisationFrame.polarisation_frames.keys():
            frame_names = PolarisationFrame(frame).names
            if sorted(names) == sorted(frame_names):
                return PolarisationFrame(frame)
    raise ValueError("Polarisation {} not supported".format(names))


def fft_griddata_to_image(griddata, template, gcf=None, wcs=None):
    """FFT griddata after applying gcf

    If imaginary is true the data array is complex

    :param griddata:
    :param gcf: Grid correction image
    :return:
    """
    # assert isinstance(griddata, GridData)

    ny, nx = (
        griddata["pixels"].data.shape[-2],
        griddata["pixels"].data.shape[-1],
    )

    if gcf is None:
        im_data = ifft(griddata["pixels"].data) * float(nx) * float(ny)
    else:
        im_data = (
            ifft(griddata["pixels"].data)
            * gcf["pixels"].data
            * float(nx)
            * float(ny)
        )
    if wcs is None:
        wcs = template.image_acc.wcs
    return create_image_from_array(
        im_data, wcs, griddata.griddata_acc.polarisation_frame
    )


def create_image_from_visibility(vis: BlockVisibility, **kwargs) -> Image:
    """Make an empty image from params and BlockVisibility

    This makes an empty, template image consistent with the visibility,
    allowing optional overriding of select parameters. This is a convenience
    function and does not transform the visibilities.

    :param vis:
    :param phasecentre: Phasecentre (Skycoord)
    :param channel_bandwidth: Channel width (Hz)
    :param cellsize: Cellsize (radians)
    :param npixel: Number of pixels on each axis (512)
    :param frame: Coordinate frame for WCS (ICRS)
    :param equinox: Equinox for WCS (2000.0)
    :param nchan: Number of image channels (Default is 1 -> MFS)
    :return: image

    See also
        :py:func:`rascil.processing_components.image.operations.create_image`
    """
    log.debug(
        "create_image_from_visibility: Parsing parameters to get definition"
        + "of WCS"
    )

    imagecentre = get_parameter(kwargs, "imagecentre", vis.phasecentre)
    phasecentre = get_parameter(kwargs, "phasecentre", vis.phasecentre)

    # Spectral processing options
    ufrequency = numpy.unique(vis["frequency"].data)
    frequency = get_parameter(kwargs, "frequency", vis["frequency"].data)

    vnchan = len(ufrequency)

    inchan = get_parameter(kwargs, "nchan", vnchan)
    reffrequency = frequency[0] * units.Hz
    channel_bandwidth = (
        get_parameter(
            kwargs, "channel_bandwidth", vis["channel_bandwidth"].data.flat[0]
        )
        * units.Hz
    )

    if (inchan == vnchan) and vnchan > 1:
        log.debug(
            "create_image_from_visibility: Defining %d channel Image at %s,"
            " starting frequency %s, and bandwidth %s"
            % (inchan, imagecentre, reffrequency, channel_bandwidth)
        )
    elif (inchan == 1) and vnchan > 1:
        assert (
            numpy.abs(channel_bandwidth) > 0.0
        ), "Channel width must be non-zero for mfs mode"
        log.debug(
            "create_image_from_visibility: Defining single channel MFS Image"
            " at %s, starting frequency %s, "
            "and bandwidth %s" % (imagecentre, reffrequency, channel_bandwidth)
        )
    elif inchan > 1 and vnchan > 1:
        assert (
            numpy.abs(channel_bandwidth) > 0.0
        ), "Channel width must be non-zero for mfs mode"
        log.debug(
            "create_image_from_visibility: Defining multi-channel MFS Image"
            " at %s, starting frequency %s, "
            "and bandwidth %s" % (imagecentre, reffrequency, channel_bandwidth)
        )
    elif (inchan == 1) and (vnchan == 1):
        assert (
            numpy.abs(channel_bandwidth) > 0.0
        ), "Channel width must be non-zero for mfs mode"
        log.debug(
            "create_image_from_visibility: Defining single channel Image"
            " at %s, starting frequency %s, "
            "and bandwidth %s" % (imagecentre, reffrequency, channel_bandwidth)
        )
    else:
        raise ValueError(
            "create_image_from_visibility: unknown spectral mode inchan = {}, "
            "vnchan = {} ".format(inchan, vnchan)
        )

    # Image sampling options
    npixel = get_parameter(kwargs, "npixel", 512)
    uvmax = numpy.max((numpy.abs(vis["uvw_lambda"].data[..., 0:2])))
    log.debug("create_image_from_visibility: uvmax = %f wavelengths" % uvmax)
    criticalcellsize = 1.0 / (uvmax * 2.0)
    log.debug(
        "create_image_from_visibility: Critical cellsize = %f radians, %f "
        "degrees" % (criticalcellsize, criticalcellsize * 180.0 / numpy.pi)
    )
    cellsize = get_parameter(kwargs, "cellsize", 0.5 * criticalcellsize)
    log.debug(
        "create_image_from_visibility: Cellsize          = %g radians, %g "
        "degrees" % (cellsize, cellsize * 180.0 / numpy.pi)
    )
    override_cellsize = get_parameter(kwargs, "override_cellsize", True)
    if (override_cellsize and cellsize > criticalcellsize) or (
        cellsize == 0.0
    ):
        log.debug(
            "create_image_from_visibility: Resetting cellsize %g radians "
            "to criticalcellsize %g radians" % (cellsize, criticalcellsize)
        )
        cellsize = criticalcellsize
    pol_frame = get_parameter(
        kwargs,
        "polarisation_frame",
        PolarisationFrame(vis._polarisation_frame),
    )
    inpol = pol_frame.npol

    # Now we can define the WCS, which is a convenient place to hold the info
    # above Beware of python indexing order! wcs and the array have opposite
    # ordering
    shape = [inchan, inpol, npixel, npixel]
    log.debug("create_image_from_visibility: image shape is %s" % str(shape))
    w = wcs.WCS(naxis=4)
    # The negation in the longitude is needed by definition of RA, DEC
    w.wcs.cdelt = [
        -cellsize * 180.0 / numpy.pi,
        cellsize * 180.0 / numpy.pi,
        1.0,
        channel_bandwidth.to(units.Hz).value,
    ]
    # The numpy definition of the phase centre of an FFT is n // 2 (0 - rel)
    # so that's what we use for
    # the reference pixel. We have to use 0 rel everywhere.
    w.wcs.crpix = [npixel // 2 + 1, npixel // 2 + 1, 1.0, 1.0]
    w.wcs.ctype = ["RA---SIN", "DEC--SIN", "STOKES", "FREQ"]
    w.wcs.crval = [
        phasecentre.ra.deg,
        phasecentre.dec.deg,
        1.0,
        reffrequency.to(units.Hz).value,
    ]
    w.naxis = 4

    w.wcs.radesys = get_parameter(kwargs, "frame", "ICRS")
    w.wcs.equinox = get_parameter(kwargs, "equinox", 2000.0)

    chunksize = get_parameter(kwargs, "chunksize", None)
    im = create_image_from_array(
        numpy.zeros(shape),
        wcs=w,
        polarisation_frame=pol_frame,
        chunksize=chunksize,
    )
    return im


def create_box_convolutionfunction(
    im, oversampling=1, support=1, polarisation_frame=None
):
    """Fill a box car function into a ConvolutionFunction

    Also returns the griddata correction function as an image

    :param im: Image template
    :param oversampling: Oversampling of the convolution function in uv space
    :return: griddata correction Image, griddata kernel as ConvolutionFunction
    """
    ##assert isinstance(im, Image)
    cf = create_convolutionfunction_from_image(
        im, oversampling=1, support=4, polarisation_frame=polarisation_frame
    )

    nchan, npol, _, _ = im["pixels"].data.shape

    cf["pixels"].data[...] = 0.0 + 0.0j
    cf["pixels"].data[..., 2, 2] = 1.0 + 0.0j

    # Now calculate the griddata correction function as an image with the same coordinates as the image
    # which is necessary so that the correction function can be applied directly to the image
    nchan, npol, ny, nx = im["pixels"].data.shape
    nu = numpy.abs(coordinates(nx))

    gcf1d = numpy.sinc(nu)
    gcf = numpy.outer(gcf1d, gcf1d)
    gcf = 1.0 / gcf

    gcf_data = numpy.zeros_like(im["pixels"].data)
    gcf_data[...] = gcf[numpy.newaxis, numpy.newaxis, ...]
    gcf_image = create_image_from_array(
        gcf_data, im.image_acc.wcs, im.image_acc.polarisation_frame
    )

    assert cf["pixels"].data.dtype == "complex", cf["pixels"].data.dtype
    assert gcf_image["pixels"].data.dtype == "float32", gcf_image[
        "pixels"
    ].data.dtype
    return gcf_image, cf
