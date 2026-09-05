# bee: themes

Eight themes. Each is one `[data-theme="name"]` block in `static/style.css` that only sets custom properties. Everything below is a proposal for Max to confirm or change; this is the main stylistic checkpoint of the build.

## variables every theme sets

```
--bg        page background
--fg        main text
--muted     secondary text
--tile      outer hexagon fill
--tile-fg   letter colour on outer hexagons
--centre    centre hexagon fill (yellow family unless noted)
--centre-fg letter colour on the centre hexagon
--accent    buttons, links, rank bar
--card      panels (found words, summary, admin table)
--font      font stack
--radius    button corner radius
```

## the eight

| theme | idea | bg | tile | centre | fg | accent | font |
|---|---|---|---|---|---|---|---|
| classic | the plain bee look | #ffffff | #e6e6e6 | #f7da21 | #111111 | #111111 | system sans |
| loveydovey | pinks, hearts, soft edges | #fff0f5 | #ffc2d4 | #ff5c8a (rose, the one proposed non yellow centre) | #6b0f2b | #d6336c | system sans, headings in a cursive fallback stack |
| midnight | dark mode | #0f172a | #1e293b | #facc15 | #e2e8f0 | #38bdf8 | system sans |
| forest | deep greens, amber centre | #0b3d2e | #2f6b4f | #d9a404 | #f1f5e9 | #9ccc65 | system sans |
| ocean | light blues | #e0f2fe | #7dd3fc | #fbbf24 | #0c4a6e | #0284c7 | system sans |
| terminal | green on black, uppercase, monospace | #000000 | #002200 with a #33ff33 1 px border | #ffff00 | #33ff33 | #33ff33 | monospace |
| newsprint | sepia paper, serif | #f4ecd8 | #d6ccb2 | #e8c547 | #222222 | #8b0000 | Georgia, serif |
| candy | pastel purples, rounded | #fdf4ff | #c4b5fd | #fde047 | #581c87 | #a21caf | "Trebuchet MS", system sans |

## theme specific touches, all optional and tiny

- loveydovey: found words prefixed with a heart, the score line reads `x words, y points, so sweet` style copy, the `enter` button labelled `send`. Hexagons get `--radius` 14 px on the input line and buttons for a soft feel.
- terminal: `text-transform: uppercase` on letters and buttons, a blinking underscore after the input line via CSS animation only.
- newsprint: the puzzle code shown like a masthead, small caps rank.
- candy: outer tiles could alternate two pastels via `:nth-child`, still all in CSS.

Anything beyond custom properties plus a handful of theme scoped selectors is out of budget. The CSS file cap is 220 lines total.

## questions for Max at the theme checkpoint

1. Keep the centre yellow in every theme, or allow loveydovey's rose centre?
2. Any of the eight to replace? The boss asked for eight "beyond the bee and minimalist original"; classic counts as one of the eight here. If he wants eight extras, drop classic from the count and add one more (proposal: `sunset`, warm oranges).
3. Rank names (see SPEC section 5) and acceptance messages (`good`, `nice`, `great`, `pangram!`).
4. Layout: board left and found words right on wide screens, stacked on mobile. Or board centred with the word list below.
