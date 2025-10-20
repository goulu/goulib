from goulib.tests import *  # pylint: disable=wildcard-import, unused-wildcard-import
from goulib.image import *  # pylint: disable=wildcard-import, unused-wildcard-import

from skimage import data
import matplotlib

import os
path = os.path.dirname(os.path.abspath(__file__))
results = os.path.join(path, 'results', 'image')  # path for results


def assert_image(image, name=None, convert=False):
    """ Checks if an image is present (not black, white, or low contrast
        :param image: Image to check
        :param name: str, optional file name. image is saved is specified
        :param convert: bool specifies if image is converted to RGB for saving
    """
    from skimage.exposure import is_low_contrast
    if name:
        image.save(os.path.join(results, name), autoconvert=convert)
    if is_low_contrast(image.array):
        logging.warning('image %s has low contrast' % name)


class TestImage(TestCase):
    @classmethod
    def setup_class(self):
        self.lena = Image(path+'/data/lena.png')
        assert self.lena == self.lena  # make sure image comparizon works
        assert_image(self.lena.grayscale('L'),
                     'grayscale.png')  # force to uint8
        self.gray = Image(os.path.join(results, 'grayscale.png'))
        self.camera = Image(data.camera())

    def test_pdf(self):
        return  # for now for speed
        try:
            import pdfminer
        except:
            return  # pass
        assert_image(Image(path+'/data/lena.pdf'), 'pdf_out.png')
        assert_image(Image(path+'/data/Pantone Fan.pdf'), 'Pantone Fan.png')
        # Image(path+'/data/Pantone Fan CMYKOGB Equinox.pdf').save('Pantone Fan CMYKOGB Equinox.png')

    def test___init__(self):
        lena2 = Image(self.lena)
        self.assertEqual(self.lena, lena2)

    def test_generate(self):
        # from matrix
        from matplotlib import cm
        a = [[-x*x+y*y for x in range(128)] for y in range(128)]
        a = normalize(a)
        assert_image(Image(a), 'generated.png')
        assert_image(Image(a, colormap=matplotlib.colormaps['nipy_spectral']),
                     'gen_colormap.png', True)

    def test___hash__(self):
        h1 = hash(self.lena)
        h2 = hash(self.gray)
        diff = h1 ^ h2  # XOR
        diff = math2.digsum(diff, 2)  # number of different pixels
        assert h1 == h2, 'difference is %d pixels' % diff

    def test_dist(self):
        assert self.lena.dist(self.gray) == 0

        s = self.lena.size
        lena2 = self.lena.resize((s[0], s[1]*2))
        lena2.save(os.path.join(results, 'lena.2.width.png'))

        tol = 4/64  # don't know why...

        d = self.lena.dist(lena2)

        assert d <= tol

        for method in [AVERAGE, PERCEPTUAL]:

            assert self.lena.dist(lena2, method) <= tol

            assert self.lena.dist(lena2.flip(), method, symmetries=True) <= tol
            assert self.lena.dist(lena2.flip(False, True),
                                  method, symmetries=True) <= tol

    def test___getitem__(self):
        pixel = self.gray[256, 256]
        assert pixel == 90
        pixel = self.lena[256, 256]
        # (180,65,72))
        assert pytest.approx(pixel) == [0.70588235, 0.25490196, 0.28235294]
        left = self.lena[:, :256]
        right = self.lena[:, 256:-1]
        face = self.lena[246:374, 225:353]
        assert_image(face, 'lena.face.png')
        face = face.grayscale()
        eye = face[3:35, -35:-3]  # negative indexes are handy in some cases
        c = face.correlation(eye)
        # assert_image(c,"correlation.png")

    def test___lt__(self):
        # image = Image(data)
        # assert_equal(expected, image.__lt__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___repr__(self):
        assert repr(self.lena) in [
            'Image(mode=RGB shape=(512, 512, 3) type=float64)',
            # with some versions
            'Image(mode=RGB shape=(512L, 512L, 3L) type=float64)',
        ]

    def test_mode(self):
        pytest.skip("not yet implemented")  # useless ?

    def test_open(self):
        lena3 = Image.open(path+'/data/lena.png')
        assert self.lena == lena3

    def test_html(self):
        # do not implement this one as it requires IPython
        pytest.skip("not yet implemented")

    def test__repr_html_(self):
        h = self.lena.convert('P')._repr_html_()
        assert h

    def test_average_hash(self):
        h1 = self.lena.average_hash()
        h2 = self.gray.average_hash()
        assert h1 == h2

    def test_perceptual_hash(self):
        h1 = self.lena.perceptual_hash()
        h2 = self.gray.perceptual_hash()
        assert h1 == h2

    def test_base64(self):
        # image = Image(data, **kwargs)
        # assert_equal(expected, image.base64(fmt))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_grayscale(self):
        pytest.skip("not yet implemented")  # TODO: implement

    def test_invert(self):
        # image = Image(data, **kwargs)
        # assert_equal(expected, image.invert())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_ndarray(self):
        pass

    def test_render(self):
        # same as h(self.lena) but without IPython
        h = self.lena.render()
        assert h

    def test_convert(self):
        for mode in modes:
            im = self.lena.convert(mode)
            assert_image(im, 'convert_%s.png' % mode)
            try:
                im2 = im.convert('RGB')
                assert_image(im2, 'convert_%s_round_trip.png' % mode)
            except Exception as e:
                logging.error(
                    '%s round trip conversion failed with %s' % (mode, e))
                im2 = im.convert('RGB')

    def test_split(self):
        rgb = self.lena.split()
        for im, c in zip(rgb, 'RGB'):
            assert_image(im, 'split_%s.tif' % c)

        assert_image(Image(rgb), 'RGB_merge.png')

        colors = ['Cyan', 'Magenta', 'Yellow', 'blacK']
        cmyk = self.lena.split('CMYK')
        cmyk2 = [im.colorize(col) for im, col in zip(cmyk, colors)]
        for im, c in zip(cmyk2, 'CMYK'):
            assert_image(im, 'split_%s.tif' % c)

        assert_image(Image(cmyk, mode='CMYK'), 'CMYK_merge.png')

        lab = self.lena.split('Lab')
        for im, c in zip(lab, 'LAB'):
            assert_image(im, 'split_%s.tif' % c)

        lab = Image(lab, mode='LAB')
        assert_image(lab, 'Lab.tif')

    def test_filter(self):
        from PIL.ImageFilter import BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN
        for f in [BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN]:
            r = self.lena.filter(f)
            assert_image(r, 'filter_pil_%s.png' % f.__name__)

        from skimage.filters import sobel, prewitt, scharr, roberts
        from skimage.restoration import denoise_bilateral
        for f in [sobel, prewitt, scharr, roberts, denoise_bilateral, ]:
            try:
                assert_image(self.lena.filter(
                    f), 'filter_sk_%s.png' % f.__name__)
            except:
                pass

    def test_dither(self):
        for k in dithering:
            im = self.gray.dither(k)*255
            assert_image(im, 'dither_%s.png' % dithering[k])
        assert_image(self.lena.dither(), 'dither_color_2.png')
        assert_image(self.lena.dither(n=4), 'dither_color_4.png')

    def test_resize(self):
        size = 128
        im = self.lena.resize((size, size))
        assert_image(im, 'resize_%d.png' % size)
        im = self.camera.resize((size, size))
        assert_image(im, 'camera_resize_%d.png' % size)

    def test_expand(self):
        size = 128
        im = self.lena.resize((size, size))
        # can you see that half pixel border ?
        im = im.expand((size+1, size+1), .5, .5)
        assert_image(im, 'expand_0.5 border.png')

    def test_add(self):
        dot = disk(20)
        im = Image()
        for i in range(3):
            for j in range(3):
                im = im.add(dot, (j*38.5, i*41.5), 0.5)
        assert_image(im, 'image_add.png')

    def test_colorize(self):
        cmyk = self.lena.split('CMYK')
        colors = ['Cyan', 'Magenta', 'Yellow', 'blacK']
        cmyk2 = [im.colorize(col) for im, col in zip(cmyk, colors)]
        # what a strange syntax ...
        back = cmyk2[0]-(-cmyk2[1])-(-cmyk2[2])-(-cmyk2[3])
        assert_image(back, 'image_add_sum_cmyk.png')
        assert self.lena.dist(back) == 0

    def test_mul(self):
        mask = disk(self.lena.size[0]/2)
        res = self.lena*mask
        assert_image(res, 'disk_mul.png')

    def test_shift(self):
        left = self.lena[:, 0:256]
        right = self.lena[:, 256:]
        blank = Image(size=(513, 513), mode='RGB', color='white')
        blank.paste(left, (0, 0))
        blank.paste(right.shift(1, 1), (256, 0))
        assert_image(blank, 'image_stitched.png')

    def test___abs__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__abs__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___add__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__add__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___div__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__div__(f))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___mul__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__mul__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___nonzero__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__nonzero__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___radd__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__radd__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___sub__(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.__sub__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_compose(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.compose(other, a, b))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_correlation(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.correlation(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_crop(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.crop(lurb))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_getdata(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.getdata(dtype))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_getpixel(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.getpixel(yx))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_load(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.load(path))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_nchannels(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.nchannels())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_normalize(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.normalize(newmax, newmin))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_npixels(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.npixels())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_paste(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.paste(image, box, mask))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_putpixel(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.putpixel(yx, value))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_quantize(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.quantize(levels))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_save(self):
        pass  # tested everywhere

    def test_scale(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.scale(s))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_shape(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.shape())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_size(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.size())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_threshold(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.threshold(level))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_getcolors(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.getcolors(maxcolors))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_getpalette(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.getpalette(maxcolors))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_setpalette(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.setpalette(p))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_new(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.new(size, color))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_pil(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.pil())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_optimize(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.optimize(maxcolors))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_replace(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.replace(pairs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_sub(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.sub(other, pos, alpha, mode))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_deltaE(self):
        # image = Image(data, mode, **kwargs)
        # assert_equal(expected, image.deltaE(other))
        pytest.skip("not yet implemented")  # TODO: implement


class TestCorrelation:
    def test_correlation(self):
        # assert_equal(expected, correlation(input, match))
        pytest.skip("not yet implemented")  # TODO: implement


class TestAlphaToColor:
    def test_alpha_to_color(self):
        # assert_equal(expected, alpha_to_color(image, color))
        pytest.skip("not yet implemented")  # TODO: implement


class TestAlphaComposite:
    def test_alpha_composite(self):
        # assert_equal(expected, alpha_composite(front, back))
        pytest.skip("not yet implemented")  # TODO: implement


class TestAlphaCompositeWithColor:
    def test_alpha_composite_with_color(self):
        # assert_equal(expected, alpha_composite_with_color(image, color))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPurePilAlphaToColorV1:
    def test_pure_pil_alpha_to_color_v1(self):
        # assert_equal(expected, pure_pil_alpha_to_color_v1(image, color))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPurePilAlphaToColorV2:
    def test_pure_pil_alpha_to_color_v2(self):
        # assert_equal(expected, pure_pil_alpha_to_color_v2(image, color))
        pytest.skip("not yet implemented")  # TODO: implement


class TestNchannels:
    def test_nchannels(self):
        # assert_equal(expected, nchannels(arr))
        pytest.skip("not yet implemented")  # TODO: implement


class TestGuessmode:
    def test_guessmode(self):
        # assert_equal(expected, guessmode(arr))
        pytest.skip("not yet implemented")  # TODO: implement


class TestAdaptRgb:
    def test_adapt_rgb(self):
        # assert_equal(expected, adapt_rgb(func))
        pytest.skip("not yet implemented")  # TODO: implement


class TestRgb2rgba:
    def test_rgb2rgba(self):
        pass  # tested in test_convert


class TestDisk:
    def test_disk(self):
        # assert_equal(expected, disk(radius, antialias))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFspecial:
    def test_fspecial(self):
        # assert_equal(expected, fspecial(name, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement


class TestReadPdf:
    def test_read_pdf(self):
        # assert_equal(expected, read_pdf(filename, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFig2img:
    def test_fig2img(self):
        # assert_equal(expected, fig2img(fig))
        pytest.skip("not yet implemented")  # TODO: implement


class TestQuantize:
    def test_quantize(self):
        # assert_equal(expected, quantize(image, N, L))
        pytest.skip("not yet implemented")  # TODO: implement


class TestDither:
    def test_dither(self):
        # assert_equal(expected, dither(image, method, N, L))
        pytest.skip("not yet implemented")  # TODO: implement


class TestGray2rgb:
    def test_gray2rgb(self):
        pass  # tested in test_convert


class TestBool2gray:
    def test_bool2gray(self):
        pass  # tested in test_convert
        pytest.skip("not yet implemented")  # TODO: implement


class TestRgba2rgb:
    def test_rgba2rgb(self):
        pass  # tested in test_convert


class TestPalette:
    def test_palette(self):
        # assert_equal(expected, palette(im, ncolors))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___init__(self):
        # palette = Palette(data, n)
        pytest.skip("not yet implemented")  # TODO: implement

    def test_index(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.index(c, dE))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_pil(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.pil())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_update(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.update(data, n))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___repr__(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_patches(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.patches(wide, size))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_sorted(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.sorted(key))
        pytest.skip("not yet implemented")  # TODO: implement


class TestLab2ind:
    def test_lab2ind(self):
        pytest.skip("not yet implemented")  # TODO: implement


class TestInd2any:
    def test_ind2any(self):
        # assert_equal(expected, ind2any(im, palette, dest))
        pytest.skip("not yet implemented")  # TODO: implement


class TestInd2rgb:
    def test_ind2rgb(self):
        # assert_equal(expected, ind2rgb(im, palette))
        pytest.skip("not yet implemented")  # TODO: implement


class TestRandomize:
    def test_randomize(self):
        # assert_equal(expected, randomize(image, N, L))
        pytest.skip("not yet implemented")  # TODO: implement


class TestDitherer:
    def test___call__(self):
        # ditherer = Ditherer(name, method)
        # assert_equal(expected, ditherer.__call__(image, N))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___init__(self):
        # ditherer = Ditherer(name, method)
        pytest.skip("not yet implemented")  # TODO: implement

    def test___repr__(self):
        # ditherer = Ditherer(name, method)
        # assert_equal(expected, ditherer.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement


class TestErrorDiffusion:
    def test___call__(self):
        # error_diffusion = ErrorDiffusion(name, positions, weights)
        # assert_equal(expected, error_diffusion.__call__(image, N))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___init__(self):
        # error_diffusion = ErrorDiffusion(name, positions, weights)
        pytest.skip("not yet implemented")  # TODO: implement


class TestFloydSteinberg:
    def test___call__(self):
        # floyd_steinberg = FloydSteinberg()
        # assert_equal(expected, floyd_steinberg.__call__(image, N))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___init__(self):
        # floyd_steinberg = FloydSteinberg()
        pytest.skip("not yet implemented")  # TODO: implement


class TestNormalize:
    def test_normalize(self):
        # assert_equal(expected, normalize(a, newmax, newmin))
        pytest.skip("not yet implemented")  # TODO: implement
