---
name: "Sổ Chi Tiêu"
description: "A calm financial control room for seeing position, spotting exceptions, and taking the next action."
colors:
  ground-light: "#f5f8f7"
  surface-light: "#ffffff"
  surface-strong-light: "#fbfdfc"
  text-light: "#142127"
  text-muted-light: "#65717d"
  line-light: "#dce4e3"
  line-soft-light: "#edf1f0"
  navigation-light: "#003f46"
  navigation-deep-light: "#002d34"
  navigation-dark: "#002e34"
  navigation-deep-dark: "#00242a"
  navigation-text: "#f2fffc"
  action-light: "#07845c"
  action-hover-light: "#006d4d"
  action-dark: "#087555"
  action-hover-dark: "#056247"
  accent-dark: "#2cc58c"
  accent-soft-light: "#e8f6f0"
  accent-soft-dark: "#173b31"
  danger-light: "#e73535"
  danger-soft-light: "#ffebea"
  danger-dark: "#ff6b6b"
  danger-soft-dark: "#432728"
  expense-current-light: "#df544a"
  expense-current-soft-light: "#fff0ee"
  expense-previous-light: "#8599a8"
  expense-decrease-light: "#2779c7"
  expense-current-dark: "#ff786f"
  expense-current-soft-dark: "#432829"
  expense-previous-dark: "#8fa2af"
  expense-decrease-dark: "#72adf0"
  expense-category-coral: "#e45b4f"
  expense-category-orange: "#f29b38"
  expense-category-purple: "#7c5ce7"
  expense-category-blue: "#3185dc"
  expense-category-pink: "#c86b98"
  expense-category-slate: "#708090"
  expense-category-burnt-orange: "#d17632"
  warning-light: "#f29b00"
  warning-foreground-light: "#8a4d00"
  warning-soft-light: "#fff7e6"
  warning-dark: "#ffb32e"
  warning-foreground-dark: "#ffc15a"
  warning-soft-dark: "#44361f"
  info-light: "#2563eb"
  info-soft-light: "#edf4ff"
  info-dark: "#74a5ff"
  info-soft-dark: "#20344d"
  assistant-analysis-coral-light: "#df5a4d"
  assistant-analysis-coral-soft-light: "#fff0ee"
  assistant-analysis-coral-dark: "#ff7b70"
  assistant-analysis-coral-soft-dark: "#422928"
  assistant-forecast-violet-light: "#7656d8"
  assistant-forecast-violet-soft-light: "#f1edff"
  assistant-forecast-violet-dark: "#ad91ff"
  assistant-forecast-violet-soft-dark: "#302948"
  ground-dark: "#0d1719"
  surface-dark: "#142124"
  surface-strong-dark: "#18272a"
  text-dark: "#e9f3f1"
  text-muted-dark: "#9eafac"
  line-dark: "#2d3d3f"
  line-soft-dark: "#223235"
typography:
  display:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "clamp(27px, 2.2vw, 34px)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "normal"
rounded:
  progress: "6px"
  compact: "8px"
  control-inner: "9px"
  control: "10px"
  inset: "12px"
  surface: "14px"
  toggle: "22px"
  circle: "50%"
spacing:
  micro: "3px"
  xs: "7px"
  sm: "10px"
  md: "14px"
  lg: "18px"
  xl: "20px"
  2xl: "24px"
  3xl: "26px"
  page-x: "34px"
components:
  button-primary-light:
    backgroundColor: "{colors.action-light}"
    textColor: "#ffffff"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "0 17px"
    height: "42px"
  button-primary-dark:
    backgroundColor: "{colors.action-dark}"
    textColor: "#ffffff"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "0 17px"
    height: "42px"
  button-outline-light:
    backgroundColor: "transparent"
    textColor: "{colors.action-light}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "38px"
  button-secondary-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "0 17px"
    height: "42px"
  input-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    typography: "{typography.body}"
    rounded: "{rounded.control-inner}"
    padding: "0 13px"
    height: "44px"
  surface-card-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.surface}"
    padding: "22px"
  report-comparison-surface-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.surface}"
    padding: "22px"
    width: "100%"
  attention-warning-light:
    backgroundColor: "{colors.warning-soft-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.inset}"
    padding: "18px"
  chip-demo-light:
    backgroundColor: "{colors.accent-soft-light}"
    textColor: "{colors.action-light}"
    typography: "{typography.label}"
    rounded: "16px"
    padding: "5px 9px"
  category-avatar-medium-light:
    backgroundColor: "color-mix(in srgb, #0da86c 13%, #ffffff)"
    textColor: "#0da86c"
    rounded: "{rounded.circle}"
    size: "43px"
  navigation-active-light:
    backgroundColor: "rgba(0, 137, 112, 0.38)"
    textColor: "#65f2cf"
    typography: "{typography.body}"
    rounded: "{rounded.control-inner}"
    padding: "0 14px"
    height: "50px"
  side-panel-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    width: "min(410px, 100%)"
  assistant-evidence-light:
    backgroundColor: "{colors.surface-strong-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.inset}"
    padding: "0 13px 13px"
    width: "100%"
  assistant-privacy-rail-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.surface}"
    padding: "17px"
    width: "250px"
  assistant-mobile-drawer-light:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.surface}"
    width: "min(320px, calc(100vw - 24px))"
---

# Design System: Sổ Chi Tiêu

## Overview

**Creative North Star: "The Calm Financial Control Room"**

Sổ Chi Tiêu is a composed operating environment for personal finance: deep-teal navigation anchors the product while warm near-white or charcoal grounds keep dense financial information calm. The interface is modern, precise, and low-noise; it makes current position legible, calls out exceptions with semantic color, and keeps the next action close.

The system is refined and restrained rather than decorative. Hierarchy comes from composition, typography, tonal separation, and softly lifted surfaces—not from ornamental borders or a wall of interchangeable tiles. Vietnamese labels remain direct and compact, while tabular numerals keep monetary comparisons stable.

**Key Characteristics:**

- Deep-teal navigation framing warm light and charcoal dark workspaces.
- Jade actions, with distinct high-contrast button fills and brighter semantic accents in dark mode.
- Composed summaries and authoritative lists that reveal exceptions before secondary detail.
- Softly elevated 14px surfaces, compact controls, and circular category or status marks.
- Focused side panels that preserve context while turning insight into action.

## Colors

The palette pairs quiet green-cast neutrals with deep-teal navigation, purposeful jade, and reserved semantic amber, red, and blue.

### Primary

- **Action Jade** (`action-light`, `action-dark`): fills primary calls to action. The dark theme uses the deeper action token for reliable white-text contrast.
- **Bright Dark Jade** (`accent-dark`): carries positive values, active states, progress, and other semantic emphasis in dark mode; it is not the dark primary-button fill.
- **Soft Jade Wash** (`accent-soft-light`, `accent-soft-dark`): supports selected controls, positive icon wells, insights, and low-intensity status regions.

### Secondary

- **Control-Room Teal** (`navigation-light`, `navigation-deep-light`, `navigation-dark`, `navigation-deep-dark`): forms the fixed navigation gradient and the mobile navigation frame in both themes.
- **Mist Navigation Text** (`navigation-text`): keeps labels and account details legible against deep teal.

### Tertiary

- **Exception Red** (`danger-light`, `danger-dark`): marks overspend, expense, deletion, and error states; its soft companion creates calm alert regions.
- **Comparison Coral** (`expense-current-light`, `expense-current-dark`): carries current-period expense totals, grouped bars, upward expense deltas, and authoritative expense values; its soft companion supports expense icon wells.
- **Previous-Period Slate** (`expense-previous-light`, `expense-previous-dark`): provides the quiet comparison series on the same scale without competing with current evidence.
- **Expense-Decrease Blue** (`expense-decrease-light`, `expense-decrease-dark`): signals a favorable downward movement while the underlying amount remains expense-colored or neutral.
- **Categorical Expense Scale** (`expense-category-coral`, `expense-category-orange`, `expense-category-purple`, `expense-category-blue`, `expense-category-pink`, `expense-category-slate`, `expense-category-burnt-orange`): distinguishes expense composition categories without borrowing income or action green.
- **Attention Amber** (`warning-light`, `warning-dark`): marks near-limit budget states without escalating them to failure. Its contrast foreground companions (`warning-foreground-light`, `warning-foreground-dark`) carry amber text and important numeric values; the brighter base amber remains available for icons, progress fills, and low-area accents.
- **Information Blue** (`info-light`, `info-dark`): identifies neutral informational states; it does not compete with jade actions.

### Neutral

- **Warm Control Ground** (`ground-light`): the light workspace canvas.
- **Charcoal Control Ground** (`ground-dark`): the dark workspace canvas.
- **Clean Surface / Charcoal Surface** (`surface-light`, `surface-dark`): the primary card, control, and panel layers.
- **Strong Surface** (`surface-strong-light`, `surface-strong-dark`): menus and inset selected contexts that need one extra tonal step.
- **Ink / Mist Ink** (`text-light`, `text-dark`): primary text with strong contrast in each theme.
- **Muted Slate** (`text-muted-light`, `text-muted-dark`): descriptions, labels, metadata, and secondary amounts.
- **Quiet Dividers** (`line-light`, `line-soft-light`, `line-dark`, `line-soft-dark`): control strokes and list separators, always subordinate to content.

### Named Rules

**The Two-Jade Rule.** In dark mode, use bright jade for semantic emphasis and the deeper action jade for white-text buttons; never substitute one for the other.

**The Exception Color Rule.** Red means failure, overspend, expense, or destructive action; amber means approaching a limit; blue means neutral information. Do not use these colors as decoration.

**The Semantic Foreground Rule.** Semantic fills and semantic text are separate jobs. Use the contrast-specific warning foreground for amber copy and financial values; reserve the base amber for icons, progress, and other low-area marks.

**The Non-Green Expense Rule.** Expense reports use coral for the current period, slate for the previous period, and a non-green categorical scale for composition. Reserve jade for income, remaining balance, positive status, navigation, and actions.

## Typography

**Display Font:** Be Vietnam Pro (with sans-serif fallback)  
**Body Font:** Be Vietnam Pro (with sans-serif fallback)

**Character:** A single contemporary Vietnamese-capable sans serif keeps the product cohesive and operational. Tight headline tracking provides authority; smaller labels stay compact without becoming cryptic.

### Hierarchy

- **Display** (700, fluid 27–34px, 1.2): page titles and the strongest first-viewport statement.
- **Headline** (700, 20px, 1.3): side-panel titles and focused task headings.
- **Title** (700, 17px, 1.35): card and section headings.
- **Body** (400, 14px, 1.5): descriptions, supporting copy, and form content.
- **Label** (600, 12px, 1.35): actions, field labels, compact status, and table metadata.
- **Amounts** (weight varies, 17–24px): use tabular numerals wherever values are compared or aligned.

### Named Rules

**The Numeric Stability Rule.** Monetary amounts, percentages, and aligned budget values use tabular numerals so changing data does not disturb the scan.

**The Financial Metadata Floor Rule.** Keep monetary context, dates, progress metadata, and audit-history text at 11–12px; never shrink this evidence below 11px to recover layout space.

## Layout

The desktop shell uses a fixed 248px sidebar and a centered work area capped at 1660px, with page padding of 36px 34px 42px. Headers are compact: title and description lead, while month, theme, and primary action controls align as a focused action cluster. Analytical pages use composed summaries, an authoritative list, and an attention rail rather than treating every datum as an equal tile.

The spacing rhythm is compact and repeated: 14–20px between related controls and rows, 20–24px inside most surfaces, and 28px between the header and content. At 1280px, dense dashboard and budget grids simplify; at 980px, navigation collapses to an 88px icon rail and two-column content becomes one column where needed. At 760px, the shell changes mode: a 66px top brand bar and fixed five-item bottom navigation frame a single-column page with safe-area-aware bottom padding. At 430px, controls and chart surfaces tighten again.

Side panels are 410px wide on larger screens and become full-width at 760px and below. Their header, scrolling body, and action footer remain separate regions so task actions stay available without losing context.

The Assistant is a bounded inquiry workspace rather than a generic page grid. On wide desktop it uses a 224px saved-history rail, a flexible conversation canvas, and a 250px data/privacy rail with 18px gaps; the canvas fills the available viewport height and keeps its composer anchored below a separately scrolling message region. At 1280px the rails tighten to 200px and 224px. At 1100px both rails leave the grid and become focus-managed drawers over the conversation; at 760px the drawer width is `min(320px, calc(100vw - 24px))`, the starters become one column, and the fixed five-destination mobile navigation keeps Assistant directly reachable.

**The Composed Hierarchy Rule.** Start analytical views with position, then exceptions, then action. Avoid mechanically repeating equal KPI cards when the data has a clearer hierarchy.

## Elevation & Depth

Depth is ambient and lifted, never hard or ornamental. Cards use a diffuse two-layer shadow over a tonal ground; menus lift slightly more; side panels use a directional shadow that communicates their right-edge origin. In dark mode the shadows deepen while surface tones do more of the separation work.

### Shadow Vocabulary

- **Ambient Card Light** (`box-shadow: 0 8px 26px rgba(18, 52, 50, 0.07), 0 2px 6px rgba(18, 52, 50, 0.045)`): resting elevation for cards and summary surfaces on the light ground.
- **Ambient Card Dark** (`box-shadow: 0 10px 28px rgba(0, 0, 0, 0.26), 0 2px 6px rgba(0, 0, 0, 0.2)`): deeper resting elevation for the charcoal workspace.
- **Floating Menu** (`box-shadow: 0 12px 28px rgba(12, 36, 35, 0.16)`): compact downward lift for contextual row menus.
- **Directional Panel Light** (`box-shadow: -12px 0 42px rgba(4, 29, 31, 0.15)`): broad left-cast separation from the light workspace.
- **Directional Panel Dark** (`box-shadow: -12px 0 42px rgba(0, 0, 0, 0.4)`): stronger left-cast separation from the dark workspace.
- **Action Lift** (`box-shadow: 0 7px 17px color-mix(in srgb, var(--button-primary) 22%, transparent)`): restrained jade-tinted lift under primary buttons, paired with a 1px upward hover movement.

### Named Rules

**The Ambient Lift Rule.** Elevation should clarify layer and action priority; it must never become a decorative glow or hard-edged frame.

## Shapes

The form language is softly geometric. Primary surfaces use a 14px radius; standard controls use 9–10px; attention and insight insets use 12px; compact links and mobile navigation items use 8px. Pills are reserved for small badges and the theme switch. Category, metric, progress, account, and status marks are circular, creating fast visual anchors inside otherwise rectilinear layouts.

Borders are quiet and mostly inset: controls use a single neutral stroke, list rows use soft dividers, and semantic attention blocks use low-opacity colored inset strokes. Imagery appears as controlled circular crops, including the shipped goal thumbnails, rather than as decorative full-bleed media.

**The Soft Geometry Rule.** Keep the 14px surface / 9–10px control relationship intact; arbitrary radii weaken the visual rhythm.

## Components

### Buttons

- **Shape:** compact, gently rounded controls (10px) with a 42px primary height and 14px semibold labels.
- **Primary:** white text on the theme-specific action fill; use the deeper dark action jade rather than bright semantic jade.
- **Hover / Focus:** rise by 1px over 160ms and darken the fill; keyboard focus uses a visible 3px jade-mixed outline with 2px offset.
- **Secondary:** surface fill, primary text, and a quiet inset neutral stroke.
- **Outline:** transparent fill with jade text and inset jade stroke; hover introduces the soft jade wash.
- **Disabled / Destructive:** disabled controls hold 50% opacity; destructive text actions use semantic red without a filled danger block.

### Chips

- **Style:** compact 11px semibold text in a jade wash with pill-like 16px corners and 5px 9px padding.
- **Use:** short contextual states such as demo data; not primary navigation or action.

### Cards / Containers

- **Corner Style:** softly elevated surfaces (14px).
- **Background:** the current theme surface token; strong surface is reserved for menus and selected inset contexts.
- **Shadow Strategy:** ambient two-layer card elevation; no hover lift is required for non-interactive containers.
- **Border:** generally none at the outer edge; use quiet internal dividers or inset strokes where structure requires them.
- **Internal Padding:** usually 20–24px, with 22px common on dashboard and category surfaces.

### Inputs / Fields

- **Style:** 44px-high surface controls with a 9px radius, 13px horizontal padding, and one neutral border.
- **Focus:** jade border plus a low-opacity 3px jade ring.
- **Error / Disabled:** errors use red text on a soft red field; disabled grouped controls reduce opacity without changing meaning.

### Navigation

Desktop navigation is a fixed deep-teal rail with 50px items, 9px corners, 15px medium labels, and 21px icons. Hover adds a translucent white wash; active items use a translucent jade field and mint text. At 980px labels and account details collapse into an icon rail. At 760px, Overview, Transactions, Reports, Assistant, and More move into a fixed five-item bottom navigation with icon-over-label items, while the brand remains in a compact top bar.

### Category Avatars

Category avatars are circular semantic anchors in 32px, 43px, and 50px sizes. Each uses the category’s own color for the icon and a 13% color mix against the current surface for the background.

### Budget Attention Items

Attention items combine a circular status icon, short explanation, and local outline action inside a 12px semantic inset. Warning, over-limit, and information states map strictly to amber, red, and blue. They explain both the condition and the next action without replacing the authoritative budget list.

### Period Comparison Reports

Period comparison is a composed evidence pattern, not a generic KPI dashboard. A single three-part summary establishes income, expense, and remaining balance; the dominant grouped chart compares current coral and previous slate on one shared scale; composition and largest movements remain supporting evidence; and a totalled detail table is the source of truth with links into filtered transactions.

- **Category Scale:** show at most six leading categories plus “Danh mục khác” in charts when the dataset exceeds seven categories. Keep every category as its own row in the detail table.
- **Overflow:** wide charts and tables live in horizontally scrollable regions with an accessible name, `tabindex="0"`, and the established visible jade focus treatment.
- **Color Semantics:** raw expense values and marks never use green. A decrease may use the expense-decrease blue signal, but the underlying monetary amount stays expense-colored or neutral.
- **Responsive Behavior:** the dominant comparison and supporting rail may collapse at compact widths, but their evidence order and the totalled source table remain intact.

### Assistant Inquiry Studio

The Assistant opens with four concrete financial jobs—expense comparison, anomaly detection, cash-flow forecasting, and planning—rather than an empty generic chatbot. Choosing a job fills the composer so the user can review or refine the question before sending; the first send creates the saved thread, and the starters then yield to the conversation.

Assistant answers keep advice and proof in the same reading path. The answer body leads, followed by an open evidence disclosure containing the selected period, current and previous expense totals, a compact category comparison table, an amber confidence note, deterministic links to Reports and filtered Transactions, and two follow-up prompts. The evidence surface uses a 12px inset radius, quiet dividers, tabular numerals, and the existing semantic expense colors; it does not imitate a free-standing report dashboard.

The right rail makes both scope and privacy persistent on desktop. It names which aggregates are used, shows freshness and transaction count, states what is excluded, and repeats that Gemini is advisory-only. Do not bury these assurances in a tooltip or one-time consent screen.

**The Guided Blank-State Rule.** A financial assistant starts from meaningful user jobs and editable example questions, never from a blank chat box as the only affordance.

**The Evidence-Beside-Advice Rule.** Every generated financial interpretation keeps its period, aggregate basis, confidence limits, and source-screen links inspectable beside the answer.

### Mobile Drawers and Navigation

Below 1100px, history and data scope become opposing edge drawers activated from the Assistant header. Each drawer uses a scrim, traps focus while open, closes on Escape, close control, or scrim activation, and restores focus to its opener. At mobile widths the drawers stop above the fixed bottom navigation so close controls, history actions, and the current destination remain reachable. The mobile navigation exposes five items—Overview, Transactions, Reports, Assistant, and More—with Assistant as a direct destination rather than hiding it inside More.

### Side Panels

Focused create and edit work happens in a right-edge panel with separate header, scrolling body, and footer. The panel traps focus, closes on Escape or scrim interaction, restores prior focus, and expands to full width on mobile. Its 300ms entrance uses the same smooth deceleration as page arrival and is removed under reduced-motion preferences.

### Profile Editing Panel

The sidebar account identity is the entry point for editing profile details without leaving the current financial task. The full account card opens the established right-edge Side Panel on desktop; the compact rail and mobile header expose the same action through a profile-edit icon. Keep the standard 410px desktop width, full-width mobile treatment, separated header/body/footer, focus trap, Escape and scrim dismissal, and focus restoration.

- **Avatar:** use a circular 82px preview with an initial fallback and controlled cover crop. Accept PNG, JPEG, or WebP files up to 2 MB; present upload/change as a secondary button and removal as a red text action.
- **Identity Fields:** keep display name optional, with username and email required because both remain sign-in identities. Use the standard 44px fields, jade focus ring, concise helper text, and inline semantic success or error feedback.
- **Actions and Continuity:** keep Close secondary and Save Changes jade-primary in the persistent footer. Disable saving until text values are dirty and while profile or avatar work is in progress; after a successful mutation, update the shared account identity immediately so the sidebar name, email, and avatar reflect the result in place.

## Do's and Don'ts

### Do:

- **Do** keep deep-teal navigation visually stable while light and dark workspace surfaces change around it.
- **Do** use the theme-specific action fill for primary buttons and reserve bright dark jade for semantic emphasis.
- **Do** make exception colors explain status and pair them with text, iconography, or position rather than color alone.
- **Do** preserve the 14px surface radius, ambient elevation, compact control scale, and Be Vietnam Pro hierarchy.
- **Do** keep Vietnamese action labels concise and place focused create/edit work in context-preserving side panels.
- **Do** collapse to the fixed five-item bottom navigation and full-width panels at the mobile breakpoint.
- **Do** aggregate long report charts into six leading categories plus “Danh mục khác” while retaining every category in the totalled detail table.
- **Do** give horizontally scrollable financial charts and tables an accessible name, keyboard focus, and a visible focus ring.
- **Do** begin Assistant with the four demonstrated financial jobs and let each starter populate an editable question before it is sent.
- **Do** keep aggregate evidence, confidence limits, privacy exclusions, and deterministic source-screen links visible wherever AI advice appears.
- **Do** turn Assistant history and data scope into focus-managed drawers below 1100px while keeping Assistant directly available in the five-item mobile navigation.

### Don't:

- **Don't** use bright `accent-dark` as the dark primary-button background; it does not provide the implemented white-text contrast.
- **Don't** flatten every overview into a generic equal KPI grid when position, exception, and action have different importance.
- **Don't** add hard decorative outlines, glossy gradients, or conspicuous hover shadows to lifted surfaces.
- **Don't** use red, amber, or blue as ambient decoration or as the sole carrier of meaning.
- **Don't** use jade or another green for expense amounts, expense bars, or expense-composition categories.
- **Don't** present AI financial advice without an inspectable period, aggregate basis, confidence statement, and path back to the underlying product screens.
- **Don't** send or imply access to raw transactions, notes, identity fields, goal names, internal IDs, or user-authored category names; the Assistant's visible privacy rail must match the aggregate-only contract.
- **Don't** promote a page-specific composition into a global template; preserve this system’s hierarchy while allowing each task surface to compose its own evidence.
