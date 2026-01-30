# /// script
# dependencies = [
#     "marimo",
#     "anywidget",
#     "traitlets",
#     "numpy==2.4.1",
#     "matplotlib==3.10.8",
# ]
# requires-python = ">=3.11"
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import anywidget
    import traitlets
    return anywidget, mo, traitlets


@app.cell
def _(anywidget, traitlets):
    class ColorSwatches(anywidget.AnyWidget):
        """A multi-swatch widget displaying multiple colors in a row, each with its own color picker."""

        _esm = """
        function loadPickrCSS() {
            if (document.getElementById('pickr-css')) return Promise.resolve();
            return new Promise((resolve) => {
                const link = document.createElement('link');
                link.id = 'pickr-css';
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/@simonwep/pickr@1.9.1/dist/themes/monolith.min.css';
                link.onload = resolve;
                document.head.appendChild(link);
            });
        }

        function loadPickrScript() {
            if (window.Pickr) return Promise.resolve(window.Pickr);
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@simonwep/pickr@1.9.1/dist/pickr.min.js';
                script.onload = () => resolve(window.Pickr);
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        async function render({ model, el }) {
            const Pickr = await loadPickrScript();
            await loadPickrCSS();

            const container = document.createElement('div');
            container.className = 'color-swatches-container';
            el.appendChild(container);

            let isUpdatingFromPickr = false;
            const swatchElements = [];
            const labelElements = [];
            const pickrInstances = [];
            const colors = model.get('colors') || ['#335791'];

            // Undo history
            const historyLength = model.get('history_length') || 10;
            const history = [];

            function saveToHistory() {
                history.push([...model.get('colors')]);
                if (history.length > historyLength) history.shift();
            }

            function undo() {
                if (history.length === 0) return;
                const previousColors = history.pop();
                isUpdatingFromPickr = true;
                model.set('colors', previousColors);
                model.save_changes();
                previousColors.forEach((color, i) => {
                    swatchElements[i].style.backgroundColor = color;
                    labelElements[i].textContent = color;
                    pickrInstances[i].setColor(color, true); // silent mode
                });
                isUpdatingFromPickr = false;
            }

            // Hover tracking for CTRL+Z
            let isHovering = false;
            container.addEventListener('mouseenter', () => { isHovering = true; });
            container.addEventListener('mouseleave', () => { isHovering = false; });

            // CTRL+Z listener
            document.addEventListener('keydown', (e) => {
                if (isHovering && e.ctrlKey && e.key === 'z') {
                    e.preventDefault();
                    undo();
                }
            });

            colors.forEach((color, index) => {
                const item = document.createElement('div');
                item.className = 'color-swatch-item';

                const label = document.createElement('span');
                label.className = 'color-swatch-label';
                label.textContent = color;
                labelElements.push(label);

                const swatch = document.createElement('div');
                swatch.className = 'color-swatch';
                swatch.style.backgroundColor = color;
                swatchElements.push(swatch);

                item.appendChild(label);
                item.appendChild(swatch);
                container.appendChild(item);

                const pickr = Pickr.create({
                    el: swatch,
                    theme: 'monolith',
                    default: color,
                    useAsButton: true,
                    components: {
                        preview: true,
                        opacity: false,
                        hue: true,
                        interaction: { hex: true, rgba: true, input: true, save: true }
                    }
                });
                pickrInstances.push(pickr);

                pickr.on('save', (colorObj) => {
                    if (colorObj) {
                        saveToHistory(); // Save state BEFORE change
                        const hex = colorObj.toHEXA().toString();
                        isUpdatingFromPickr = true;
                        const currentColors = [...model.get('colors')];
                        currentColors[index] = hex;
                        model.set('colors', currentColors);
                        model.save_changes();
                        swatch.style.backgroundColor = hex;
                        label.textContent = hex;
                        isUpdatingFromPickr = false;
                    }
                    pickr.hide();
                });
            });

            model.on('change:colors', () => {
                if (isUpdatingFromPickr) return;
                const newColors = model.get('colors');
                newColors.forEach((color, index) => {
                    if (index < pickrInstances.length) {
                        pickrInstances[index].setColor(color);
                        swatchElements[index].style.backgroundColor = color;
                        labelElements[index].textContent = color;
                    }
                });
            });
        }

        export default { render };
        """

        _css = """
        .color-swatches-container {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
        }
        .color-swatch-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }
        .color-swatch-label {
            font-family: monospace;
            font-size: 11px;
            color: #333;
        }
        .dark .color-swatch-label,
        .dark-theme .color-swatch-label {
            color: #e0e0e0;
        }
        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 6px;
            border: 2px solid #e0e0e0;
            cursor: pointer;
            transition: transform 0.1s ease;
        }
        .color-swatch:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        """

        colors = traitlets.List(traitlets.Unicode()).tag(sync=True)
        history_length = traitlets.Int(10).tag(sync=True)

        def __init__(self, colors="#335791", history_length=10, **kwargs):
            if isinstance(colors, str):
                colors = [colors]
            super().__init__(colors=colors, history_length=history_length, **kwargs)
    return (ColorSwatches,)


@app.cell
def _(mo):
    mo.md(r"""
    # Matplotlib Color Palette Tool

    Click on any swatch to open the color picker. The generated `axes.prop_cycle` updates reactively.

    **Tip:** Hover over the swatches and press `Ctrl+Z` to undo changes (up to 10 steps).
    """)
    return


@app.cell
def _(ColorSwatches, mo):
    default_colors = [
        '#335791', '#db4e4e', '#f68e59', '#cba6f7', '#a6e3a1',
        '#f38ba8', '#99d1db', '#ffd072', '#f4b8e4'
    ]
    swatches = mo.ui.anywidget(ColorSwatches(colors=default_colors))
    swatches
    return (swatches,)


@app.cell
def _(mo, swatches):
    hex_codes = [c.lstrip('#') for c in swatches.colors]
    prop_cycle = f"axes.prop_cycle: cycler('color', {hex_codes})"
    mo.md(f"""
    ### Generated Style

    ```
    {prop_cycle}
    ```
    """)
    return


@app.cell
def _(swatches):
    def plot_test():
        import numpy as np
        import matplotlib.pyplot as plt

        x = np.linspace(0, 2*np.pi, 360)
        y = np.sin(x)

        fig, ax = plt.subplots()

        for i, c in enumerate(swatches.colors):
            ax.plot(x, i + y, c=c)

        plt.xlabel('$\\theta$ [rad]')
        plt.ylabel('$y$')
        plt.title('Color Theme Test')

        return fig
    return (plot_test,)


@app.cell
def _(mo, plot_test):
    mo.center(plot_test())
    return


if __name__ == "__main__":
    app.run()
