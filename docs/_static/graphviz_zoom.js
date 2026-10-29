/**
 * Interactive pan and zoom controller for Sphinx Graphviz inheritance diagrams.
 */
document.addEventListener('DOMContentLoaded', function () {
    const containers = document.querySelectorAll('div.graphviz');

    containers.forEach(function (container) {
        if (container.dataset.zoomInitialized) return;
        container.dataset.zoomInitialized = 'true';

        const obj = container.querySelector('object.graphviz, img.graphviz');
        if (!obj) return;

        // Create wrapper structure
        const wrapper = document.createElement('div');
        wrapper.className = 'graphviz-wrapper';

        const toolbar = document.createElement('div');
        toolbar.className = 'graphviz-toolbar';

        const viewport = document.createElement('div');
        viewport.className = 'graphviz-viewport';

        // Insert wrapper into DOM
        container.parentNode.insertBefore(wrapper, container);
        wrapper.appendChild(toolbar);
        wrapper.appendChild(viewport);
        viewport.appendChild(container);

        // Toolbar controls
        const btnZoomOut = document.createElement('button');
        btnZoomOut.innerHTML = '&#8722;';
        btnZoomOut.title = 'Zoom out (-15%)';

        const btnZoomIn = document.createElement('button');
        btnZoomIn.innerHTML = '&#43;';
        btnZoomIn.title = 'Zoom in (+15%)';

        const zoomText = document.createElement('span');
        zoomText.className = 'zoom-level-text';
        zoomText.textContent = '100%';

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.className = 'zoom-slider';
        slider.min = '25';
        slider.max = '300';
        slider.step = '5';
        slider.value = '100';
        slider.title = 'Zoom level';

        const btnReset = document.createElement('button');
        btnReset.textContent = '100%';
        btnReset.title = 'Actual size (100%)';

        const btnFit = document.createElement('button');
        btnFit.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px;"><path d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>';
        btnFit.title = 'Fit to width';

        const btnFullscreen = document.createElement('button');
        btnFullscreen.innerHTML = '&#x26F6;';
        btnFullscreen.title = 'Fullscreen';

        toolbar.appendChild(btnZoomOut);
        toolbar.appendChild(slider);
        toolbar.appendChild(btnZoomIn);
        toolbar.appendChild(zoomText);
        toolbar.appendChild(btnReset);
        toolbar.appendChild(btnFit);
        toolbar.appendChild(btnFullscreen);

        let baseW = 1200;
        let baseH = 1600;
        let currentZoom = 1.0;

        function getSvgNaturalDimensions() {
            try {
                if (obj.contentDocument) {
                    const svg = obj.contentDocument.querySelector('svg');
                    if (svg) {
                        if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width > 0) {
                            baseW = svg.viewBox.baseVal.width * (4 / 3);
                            baseH = svg.viewBox.baseVal.height * (4 / 3);
                            return true;
                        }
                        const wAttr = svg.getAttribute('width');
                        const hAttr = svg.getAttribute('height');
                        if (wAttr && hAttr) {
                            baseW = parseFloat(wAttr) * (wAttr.includes('pt') ? 4 / 3 : 1);
                            baseH = parseFloat(hAttr) * (hAttr.includes('pt') ? 4 / 3 : 1);
                            return true;
                        }
                    }
                }
            } catch (err) {
                // Cross-origin fallback
            }
            if (obj.offsetWidth && obj.offsetHeight) {
                baseW = obj.offsetWidth;
                baseH = obj.offsetHeight;
                return true;
            }
            return false;
        }

        function setZoom(factor, pivotX, pivotY) {
            factor = Math.max(0.2, Math.min(3.5, factor));
            const oldZoom = currentZoom;
            currentZoom = factor;

            const scrollL = viewport.scrollLeft;
            const scrollT = viewport.scrollTop;

            const newW = Math.round(baseW * currentZoom);
            const newH = Math.round(baseH * currentZoom);

            obj.style.width = newW + 'px';
            obj.style.height = newH + 'px';

            zoomText.textContent = Math.round(currentZoom * 100) + '%';
            slider.value = Math.round(currentZoom * 100);

            if (pivotX !== undefined && pivotY !== undefined && oldZoom > 0) {
                const ratio = currentZoom / oldZoom;
                viewport.scrollLeft = (scrollL + pivotX) * ratio - pivotX;
                viewport.scrollTop = (scrollT + pivotY) * ratio - pivotY;
            }
        }

        function fitToWidth() {
            const padding = 40;
            const availableW = viewport.clientWidth - padding;
            if (availableW > 0 && baseW > 0) {
                setZoom(availableW / baseW);
            }
        }

        function initDimensionsAndApply() {
            getSvgNaturalDimensions();
            fitToWidth();
        }

        // Try initializing when object loads or immediately
        if (obj.tagName.toLowerCase() === 'object') {
            obj.addEventListener('load', initDimensionsAndApply);
        }
        initDimensionsAndApply();
        setTimeout(initDimensionsAndApply, 200);
        setTimeout(initDimensionsAndApply, 800);

        // Button handlers
        btnZoomOut.addEventListener('click', function () {
            setZoom(currentZoom - 0.15);
        });

        btnZoomIn.addEventListener('click', function () {
            setZoom(currentZoom + 0.15);
        });

        slider.addEventListener('input', function () {
            setZoom(parseFloat(slider.value) / 100);
        });

        btnReset.addEventListener('click', function () {
            setZoom(1.0);
        });

        btnFit.addEventListener('click', function () {
            fitToWidth();
        });

        btnFullscreen.addEventListener('click', function () {
            if (!document.fullscreenElement) {
                wrapper.requestFullscreen().catch(function () {});
            } else {
                document.exitFullscreen().catch(function () {});
            }
        });

        // Mouse wheel zoom (with Ctrl or Alt, or standard wheel over viewport)
        viewport.addEventListener('wheel', function (e) {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                const rect = viewport.getBoundingClientRect();
                const pivotX = e.clientX - rect.left;
                const pivotY = e.clientY - rect.top;
                const factor = e.deltaY < 0 ? currentZoom * 1.15 : currentZoom * 0.87;
                setZoom(factor, pivotX, pivotY);
            }
        }, { passive: false });

        // Pan by dragging
        let isPanning = false;
        let startX = 0;
        let startY = 0;
        let scrollStartLeft = 0;
        let scrollStartTop = 0;

        viewport.addEventListener('mousedown', function (e) {
            // Only drag on primary button
            if (e.button !== 0) return;
            isPanning = true;
            viewport.classList.add('panning');
            startX = e.clientX;
            startY = e.clientY;
            scrollStartLeft = viewport.scrollLeft;
            scrollStartTop = viewport.scrollTop;
        });

        window.addEventListener('mousemove', function (e) {
            if (!isPanning) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            viewport.scrollLeft = scrollStartLeft - dx;
            viewport.scrollTop = scrollStartTop - dy;
        });

        window.addEventListener('mouseup', function () {
            if (isPanning) {
                isPanning = false;
                viewport.classList.remove('panning');
            }
        });
    });
});
