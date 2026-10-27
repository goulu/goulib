import pytest
from goulib.tests import *
from goulib.markup import *
from goulib.markup import _oneliner, _totuple, _argsdicts


class TestCgiprint:
    def test_cgiprint(self, capsys):
        cgiprint("hello", unbuff=True, line_end="\n")
        captured = capsys.readouterr()
        assert captured.out == "hello\n"


class TestTag:
    def test_tag(self):
        t = tag('tag', 'between', class_='class')
        assert t == '<tag class="class">between</tag>'

        t = tag('tag', u'b\xc3\xa9twe\xc3\xaa\xc3\xb1', class_='class')
        assert t == '<tag class="class">b&#195;&#169;twe&#195;&#170;&#195;&#177;</tag>'

        t = tag('tag', None, style={'align': 'left', 'color': 'red'}, single=True)
        assert t in (
            '<tag style="color:red; align:left;" />',
            '<tag style="align:left; color:red;" />',
        )

        t = tag('test', r'$\left(x\right)$')
        assert t == r'<test>$\left(x\right)$</test>'

        # None value attribute (e.g. checked)
        t = tag('input', None, checked=None, single=True)
        assert 'checked' in t
        assert t == '<input checked />'

        # Special attribute names
        t = tag('meta', None, http_equiv='content-type', single=True)
        assert 'http-equiv="content-type"' in t
        t = tag('form', 'content', accept_charset='utf-8')
        assert 'accept-charset="utf-8"' in t


class TestElement:
    def test_element_calls(self, capsys):
        e_lower = element('div', case='lower')
        e_upper = element('div', case='upper')
        e_given = element('MyTag', case='given')
        assert e_lower.tag == 'div'
        assert e_upper.tag == 'DIV'
        assert e_given.tag == 'MyTag'

        # Standalone element without parent
        out = e_lower('content', id='d1')
        assert out == '<div id="d1">content</div>'

        out_single = element('img', case='lower')(src='pic.png')
        assert out_single == '<img src="pic.png" />'

        # Element with parent
        p = page(mode='strict_html')
        p.class_ = 'global_cls'
        el = element('p', parent=p)
        el('text')
        captured = capsys.readouterr()
        assert '<p class="global_cls">text</p>' in captured.out

        # Opening & closing
        el.open()
        el.close()
        captured = capsys.readouterr()
        assert '<p>' in captured.out
        assert '</p>' in captured.out

        # Single tag closing error
        br_el = element('br', parent=p)
        with pytest.raises(ClosingError):
            br_el('cannot have body')
        with pytest.raises(ClosingError):
            br_el.close()

        # Deprecated tag error in strict mode
        font_el = element('font', parent=p)
        with pytest.raises(DeprecationError):
            font_el('old')
        with pytest.raises(DeprecationError):
            font_el.open()
        with pytest.raises(DeprecationError):
            font_el.close()

        # Invalid element error
        bad_el = element('nonexistent_tag_xyz', parent=p)
        with pytest.raises(InvalidElementError):
            bad_el('content')


class TestPage:
    def test_page_modes(self):
        p_strict = page(mode='strict_html')
        assert p_strict.mode == 'strict_html'

        p_loose = page(mode='loose_html')
        assert p_loose.mode == 'loose_html'
        # Deprecated elements work in loose_html
        p_loose.center('centered')

        with pytest.raises(ModeError):
            page(mode='invalid_mode')

        # XML mode
        p_xml = page(mode='xml')
        assert 'any_tag' in p_xml.twotags
        p_xml_custom = page(mode='xml', onetags=['br'], twotags=['p'])
        assert p_xml_custom.onetags == ['br']
        with pytest.raises(CustomizationError):
            page(mode='xml', onetags=['br'])

    def test_page_content_and_init(self, capsys):
        p = page(mode='strict_html')
        p.init(
            title='My Title',
            lang='fr',
            css='style.css',
            metainfo={'author': 'Tester'},
            script={'app.js': 'javascript'},
            header='Header',
            footer='Footer'
        )
        p.p('Hello World')
        p.add('Additional')
        p.addheader('Top')
        p.addfooter('Bottom')

        res_str = str(p)
        assert 'Footer' in res_str
        assert 'Bottom' in res_str

        escaped = p(escape=True)
        assert '&lt;' in escaped or len(escaped) > 0

    def test_page_attributes(self):
        p = page()
        # Reserved keyword handling with leading underscore
        div = p.div('Content')
        # Private dunder raises AttributeError
        with pytest.raises(AttributeError):
            getattr(p, '__private__')
        # Non-keyword single underscore raises AttributeError
        with pytest.raises(AttributeError):
            getattr(p, '_not_a_keyword')


class TestEscape:
    def test_escape(self):
        assert escape('<>&"\'\n', newline=True) == '&lt;&gt;&amp;&quot;&quot;<br>'
        assert escape(123) == 123


class TestUnescape:
    def test_unescape(self):
        assert unescape('&lt;&gt;&amp;&quot;') == '<>&"'
        assert unescape(123) == 123


class TestRussell:
    def test_russell(self):
        r = russell()
        assert 'anything' in r
        assert 123 in r


class TestErrors:
    def test_errors(self):
        ce = ClosingError('img')
        assert 'img' in str(ce)
        oe = OpeningError('br')
        assert 'br' in str(oe)
        ae = ArgumentError('tag')
        assert 'tag' in str(ae)
        ie = InvalidElementError('foo', 'strict')
        assert 'foo' in str(ie)
        de = DeprecationError('font')
        assert 'font' in str(de)
        me = ModeError('wrong')
        assert 'wrong' in str(me)
        cue = CustomizationError()
        assert 'onetags' in str(cue)


class TestStyleHelpers:
    def test_style_dict2str(self):
        s = style_dict2str({'color': 'red', 'margin': '10px'})
        assert 'color:red;' in s
        assert 'margin:10px;' in s

    def test_style_str2dict(self):
        d = style_str2dict('color: red; margin: 10px; invalid')
        assert d == {'color': 'red', 'margin': '10px'}
        assert style_str2dict('') == {}
        assert style_str2dict(None) == {}


class TestOneliner:
    def test_oneliner(self):
        o = _oneliner(case='lower')
        assert o.p('test') == '<p>test</p>'
        uo = _oneliner(case='upper')
        assert uo.p('test') == '<P>test</P>'
        with pytest.raises(AttributeError):
            getattr(o, '__bad__')
        with pytest.raises(AttributeError):
            getattr(o, '_bad')
        # multiple args / lists
        res = oneliner.li(['item1', 'item2'])
        assert '<li>item1</li>\n<li>item2</li>' == res
