# Design QA — Hizmet Referans Kartları

- Source visual truth: `C:\Users\me\AppData\Local\Temp\codex-clipboard-3e020136-aa8a-475f-b935-cb130b7254e4.png`
- Implementation screenshots: `D:\Projeler\ekosan\design-qa-implementation.png`, `D:\Projeler\ekosan\design-qa-mobile.png`
- Desktop comparison: source 2048 × 739 px; implementation capture 1074 × 714 px from a 1920 × 900 CSS viewport override. Browser output was display-scaled; layout was judged from the visible three-card desktop state and DOM geometry.
- Mobile comparison: implementation capture 370 × 824 px from a 390 × 844 CSS viewport.
- State: service reference carousel; first item has YouTube, remaining items have no video.

## Findings

- No actionable P0/P1/P2 mismatch remains.
- Typography: heading hierarchy, bold card titles, orange category label and supporting copy match the existing Ekosan visual language.
- Spacing/layout: cards use a consistent 16:9 thumbnail ratio, equal-height content alignment, stable gaps and responsive one/two/three-card behavior.
- Colors/tokens: white section, slate title, blue underline, dark overlay, orange reference label and white play control are consistent with the supplied reference.
- Image quality: production images retain `object-cover`, responsive sources and explicit 768 × 432 dimensions. Preview fixtures intentionally returned missing images, so crop sharpness must be rechecked with production uploads after deployment.
- Copy/content: reference title and subtitle remain admin-managed. Video controls appear only for a valid YouTube URL.

## Interaction Evidence

- YouTube modal opened from the first reference card.
- Privacy-enhanced iframe URL was populated only on click.
- Close button and Escape/backdrop handling were implemented; close button was exercised successfully.
- Mobile modal and close control were visible.
- Browser console: no errors or warnings from the page.

## Comparison History

1. Initial capture found the newly added play control rendered too narrow because the generated Tailwind bundle did not yet include the new utility classes.
2. Rebuilt `site.min.css`; post-fix desktop capture shows the intended circular play button and balanced card spacing.
3. Mobile capture confirmed a single full-width 16:9 card without horizontal page overflow.

## Follow-up Polish

- P3: Recheck real production thumbnail focal points after editors upload final 16:9 covers.

final result: passed
