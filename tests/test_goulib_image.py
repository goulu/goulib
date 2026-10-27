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
        self.small = self.lena.resize((32, 32))
        self.gray_small = self.gray.resize((64, 64))
        self.p = self.small.convert('P')

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
        small = self.lena.resize((10, 10))
        assert small < self.lena

    def test___repr__(self):
        assert repr(self.lena) in [
            'Image(mode=RGB shape=(512, 512, 3) type=float64)',
            # with some versions
            'Image(mode=RGB shape=(512L, 512L, 3L) type=float64)',
        ]

    def test_mode(self):
        assert self.lena.mode == 'RGB'
        assert self.gray.mode == 'L'

    def test_open(self):
        lena3 = Image.open(path+'/data/lena.png')
        assert self.lena == lena3

    def test_html(self):
        # do not implement this one as it requires IPython
        pytest.skip("not yet implemented")

    def test__repr_html_(self):
        h = self.p._repr_html_()
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
        pytest.skip("not yet implemented")

    def test_grayscale(self):
        assert self.lena.grayscale() is not None
        assert self.lena.grayscale('L') is not None

    def test_invert(self):
        inv = self.gray.invert()
        assert inv is not None
        assert -self.gray is not None
        assert ~self.gray is not None

    def test_ndarray(self):
        pass

    def test_render(self):
        # same as h(self.lena) but without IPython
        h = self.lena.render()
        assert h

    def test_convert(self):
        for mode in modes:
            im = self.small.convert(mode)
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
            im = self.gray_small.dither(k)*255
            assert_image(im, 'dither_%s.png' % dithering[k])
        assert_image(self.small.dither(), 'dither_color_2.png')
        assert_image(self.small.dither(n=4), 'dither_color_4.png')

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
        assert abs(self.gray) > 0

    def test___add__(self):
        im = self.gray + self.gray
        assert im is not None

    def test___div__(self):
        im = self.gray / 2
        assert im is not None

    def test___mul__(self):
        im1 = self.gray * 0.5
        im2 = self.gray * 'red'
        im3 = self.gray * disk(self.gray.size[0] / 2)
        assert im1 is not None and im2 is not None and im3 is not None

    def test___nonzero__(self):
        assert bool(self.lena)
        assert bool(self.gray)

    def test___radd__(self):
        im = 0 + self.gray
        assert im == self.gray

    def test___sub__(self):
        im = self.gray - self.gray
        assert im is not None

    def test_compose(self):
        im = self.gray.compose(self.gray, 0.3, 0.7)
        assert im is not None

    def test_correlation(self):
        c = self.gray.correlation(disk(5))
        assert c is not None

    def test_crop(self):
        c = self.lena.crop((0, 0, 10, 10))
        assert c.size == (10, 10)

    def test_getdata(self):
        d1 = self.gray.getdata(float)
        d2 = self.gray.getdata(np.uint8)
        d3 = self.gray.getdata(np.int16)
        d4 = self.gray.getdata(np.uint16)
        assert d1 is not None and d2 is not None and d3 is not None and d4 is not None

    def test_getpixel(self):
        p1 = self.gray.getpixel((10, 10))
        p2 = self.lena.getpixel((10, 10))
        assert p1 is not None and p2 is not None

    def test_load(self):
        im = Image()
        im.load(path + '/data/lena.png')
        assert im.size == (512, 512)

    def test_nchannels(self):
        assert self.gray.nchannels == 1
        assert self.lena.nchannels == 3

    def test_normalize(self):
        arr = normalize(self.gray.getdata(float), 100, 0)
        assert arr.max() <= 100
        arr_rgb = normalize(self.lena.array, 100, 0)
        assert arr_rgb.max() <= 100

    def test_npixels(self):
        assert self.gray.npixels == 512 * 512

    def test_paste(self):
        im = Image(self.gray)
        sub = disk(10)
        im.paste(sub, (20, 20))
        assert im is not None

    def test_putpixel(self):
        im1 = Image(self.gray)
        im1.putpixel((5, 5), 128)
        assert im1.getpixel((5, 5)) == 128
        im2 = Image(self.lena)
        im2.putpixel((5, 5), Gcolors.Color('blue'))
        assert im2 is not None

    def test_quantize(self):
        q = self.gray.quantize(16)
        assert q is not None

    def test_save(self):
        pass  # tested everywhere

    def test_scale(self):
        s1 = self.lena.scale(0.5)
        s2 = self.lena.scale((0.5, 0.5))
        assert s1.size == (256, 256)
        assert s2.size == (256, 256)
        sp = self.p.scale(2)
        assert sp is not None

    def test_shape(self):
        assert self.gray.shape == (512, 512, 1)
        assert self.lena.shape == (512, 512, 3)

    def test_size(self):
        assert self.gray.size == (512, 512)
        assert self.gray.width == 512
        assert self.gray.height == 512
        assert self.gray.ratio == 1.0

    def test_threshold(self):
        t1 = self.gray.threshold(100)
        t2 = self.gray.threshold()
        assert t1 is not None and t2 is not None

    def test_getcolors(self):
        c = list(self.small.getcolors(16))
        assert len(c) > 0

    def test_getpalette(self):
        assert self.p.getpalette() is not None
        assert self.small.getpalette(16) is not None

    def test_setpalette(self):
        pal = self.p.palette
        self.p.setpalette(pal)
        assert self.p.palette == pal

    def test_new(self):
        im = Image.new('RGB', (10, 10), 'blue')
        assert im.size == (10, 10)

    def test_pil(self):
        assert self.lena.pil is not None
        assert self.p.pil is not None

    def test_optimize(self):
        opt = Image(self.p).optimize(16)
        assert opt is not None

    def test_replace(self):
        p = Image(self.p)
        p.replace([(0, 1)])
        assert p is not None

    def test_sub(self):
        s = self.gray.sub(self.gray)
        assert s is not None

    def test_deltaE(self):
        d = self.lena.deltaE(self.lena)
        assert d is not None


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
        im1 = Image.new('RGBA', (10, 10), 'red').pil
        im2 = Image.new('RGBA', (10, 10), 'blue').pil
        assert alpha_composite(im1, im2) is not None


class TestAlphaCompositeWithColor:
    def test_alpha_composite_with_color(self):
        im = Image.new('RGBA', (10, 10), 'red').pil
        assert alpha_composite_with_color(im, (255, 255, 255)) is not None


class TestPurePilAlphaToColorV1:
    def test_pure_pil_alpha_to_color_v1(self):
        im = Image.new('RGBA', (10, 10), 'red').pil
        assert pure_pil_alpha_to_color_v1(im, (255, 255, 255)) is not None


class TestPurePilAlphaToColorV2:
    def test_pure_pil_alpha_to_color_v2(self):
        im = Image.new('RGBA', (10, 10), 'red').pil
        assert pure_pil_alpha_to_color_v2(im, (255, 255, 255)) is not None


class TestNchannels:
    def test_nchannels(self):
        assert nchannels(np.zeros((10, 10))) == 1
        assert nchannels(np.zeros((10, 10, 3))) == 3


class TestGuessmode:
    def test_guessmode(self):
        assert guessmode(np.zeros((10, 10), dtype=bool)) == '1'
        assert guessmode(np.ones((10, 10), dtype=np.uint8) * 100) == 'L'
        assert guessmode(np.zeros((10, 10, 3), dtype=np.uint8)) == 'RGB'


class TestAdaptRgb:
    def test_adapt_rgb(self):
        pytest.skip("not yet implemented")


class TestRgb2rgba:
    def test_rgb2rgba(self):
        arr = rgb2rgba(np.zeros((5, 5, 3), dtype=np.uint8))
        assert arr.shape == (5, 5, 4)
        assert rgb2rgba(arr) is arr  # already RGBA


class TestDisk:
    def test_disk(self):
        d = disk(10)
        assert d.size == (20, 20)


class TestFspecial:
    def test_fspecial(self):
        d = fspecial('disk', radius=5)
        assert d is not None


class TestReadPdf:
    def test_read_pdf(self):
        im = read_pdf(path + '/data/lena.pdf')
        assert im is not None


class TestFig2img:
    def test_fig2img(self):
        pytest.skip("not yet implemented")


class TestQuantize:
    def test_quantize(self):
        arr = quantize(np.zeros((10, 10), dtype=np.uint8), 2)
        assert arr is not None


class TestDither:
    def test_dither(self):
        arr = dither(np.zeros((10, 10), dtype=np.uint8), FLOYDSTEINBERG, 2)
        assert arr is not None


class TestGray2rgb:
    def test_gray2rgb(self):
        pass  # tested in test_convert


class TestBool2gray:
    def test_bool2gray(self):
        arr = bool2gray(np.ones((5, 5), dtype=bool))
        assert arr.max() == 255


class TestRgba2rgb:
    def test_rgba2rgb(self):
        pass  # tested in test_convert


class TestPalette:
    def test_palette(self):
        data = np.zeros((10, 10, 3), dtype=float)
        data[5:] = 100.0
        pal = palette(data, 2)
        assert len(pal) == 2


class TestLab2ind:
    def test_lab2ind(self):
        data = np.zeros((10, 10, 3), dtype=float)
        data[5:] = 100.0
        im, pal = lab2ind(data, colors=2)
        assert im.shape == (10, 10)
        assert len(pal) == 2


class TestInd2any:
    def test_ind2any(self):
        im = np.zeros((5, 5), dtype=int)
        pal = Gcolors.Palette(['red', 'blue'])
        res = ind2any(im, pal, 'rgb')
        assert res.shape == (5, 5, 3)


class TestInd2rgb:
    def test_ind2rgb(self):
        im = np.zeros((5, 5), dtype=int)
        pal = Gcolors.Palette(['red', 'blue'])
        rgb = ind2rgb(im, pal)
        assert rgb.shape == (5, 5, 3)


class TestRandomize:
    def test_randomize(self):
        arr = np.zeros((10, 10), dtype=float)
        res = randomize(arr, 2)
        assert res.shape == (10, 10)


class TestDitherer:
    def test___call__(self):
        d = Ditherer('custom', quantize)
        arr = np.zeros((10, 10), dtype=np.uint8)
        assert d(arr, 2) is not None
        assert repr(d) == 'custom'


class TestErrorDiffusion:
    def test___call__(self):
        ed = ErrorDiffusion('ed', [(0, 1), (1, 0)], [1, 1])
        arr = np.zeros((10, 10), dtype=float)
        res = ed(arr, 2)
        assert res.shape == (10, 10)


class TestFloydSteinberg:
    def test___call__(self):
        fs = FloydSteinberg()
        arr = np.zeros((10, 10), dtype=float)
        res = fs(arr, 2)
        assert res.shape == (10, 10)


class TestNormalize:
    def test_normalize(self):
        arr = normalize([[0, 10], [20, 30]], 255, 0)
        assert arr.max() == 255
        assert arr.min() == 0
