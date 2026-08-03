# Vellichor — Design System

Version: 1.0

Last Updated: August 2026

---

# Purpose

The Brand Philosophy defines how Vellichor should make users feel.

The Visual Direction defines the world Vellichor exists in.

This Design System translates those ideas into practical design rules that every interface, component, and future feature must follow.

Rather than making design decisions page by page, Vellichor follows a single, consistent design language.

Every new component should inherit these principles.

---

# Core Design Principles

Every visual decision should reinforce the following qualities:

- Calm
- Timeless
- Comfortable
- Elegant
- Intentional
- Crafted
- Human
- Premium

The interface should never seek attention.

Instead, it should quietly reward interaction through exceptional craftsmanship.

---

# Color System

## Philosophy

Vellichor does not rely on bright colors to create visual interest.

Instead, color is used with restraint to create hierarchy, warmth, and emotional comfort.

The application should feel like a premium workspace rather than a colorful dashboard.

---

## Primary Palette

The interface primarily consists of neutral matte tones.

Examples include:

- Deep Charcoal
- Matte Graphite
- Stone Gray
- Warm Ivory

These colors form the visual foundation of the application.

---

## Accent Philosophy

Accent colors should be earned.

They should never dominate the interface.

Accent colors are reserved for:

- Primary actions
- Active conversation
- Focus states
- Upload progress
- Important highlights
- Special moments

The absence of constant accent colors makes their appearance feel meaningful.

---

## Accent Direction

The preferred visual direction combines:

- Warm Graphite
- Soft Champagne
- Muted Sage

Champagne should never appear flashy or metallic.

Instead, it should resemble premium brushed aluminum or Apple's Starlight finish.

Sage should communicate calmness rather than nature.

Both accents should remain subtle.

---

## Semantic Colors

Semantic colors should remain muted.

Success

Muted Sage

Warning

Soft Amber

Error

Dusty Rose

Information

Soft Slate Blue

No neon colors should ever appear.

---

# Typography

## Philosophy

Vellichor is a reading-first application.

Typography should maximize comfort during long reading sessions.

Readability always takes priority over uniqueness.

---

## Primary Font

Inter

Used for:

- Navigation
- Sidebar
- Chat
- Buttons
- Inputs
- Headings
- Paragraphs

The application should primarily rely on a single font family.

---

## Code Font

JetBrains Mono

Used only for:

- Code blocks
- Technical snippets
- AI-generated code

---

## Display Font

None for Version 1.

Landing pages may experiment with branding typography later.

Inside the application, consistency takes priority.

---

## Typography Philosophy

Creativity comes from:

- Hierarchy
- Weight
- Spacing
- Layout

Not from unusual fonts.

---

# Spacing System

Vellichor follows an 8-point spacing system.

Preferred spacing scale:

4

8

12

16

24

32

48

64

96

Random spacing values should be avoided.

Consistent spacing creates visual rhythm and reduces cognitive load.

Whitespace should be treated as an active design element rather than empty space.

---

# Border Radius

Vellichor follows a Soft Premium Radius System.

Recommended values:

8px

Badges

12px

Buttons

16px

Inputs

20px

Cards

24px

Modals

999px

Pills

Larger surfaces receive slightly larger radii to reinforce hierarchy.

Rounded corners should feel welcoming without appearing playful.

---

# Elevation System

## Philosophy

Depth should be discovered rather than announced.

Shadows should rarely be consciously noticed.

Instead, they should quietly communicate hierarchy.

---

## Elevation Levels

Level 0

Foundation

Main workspace

No visible shadow.

---

Level 1

Resting Surface

Sidebar

Input container

Very subtle separation.

---

Level 2

Interactive Surface

Cards

Buttons

Upload area

Conversation items

Gentle depth.

---

Level 3

Floating Surface

Dropdowns

Tooltips

Context menus

Clearly above the workspace.

---

Level 4

Modal Surface

Dialogs

Delete confirmation

Settings

Highest elevation.

Background softens while the modal comes into focus.

---

## Hover Behavior

Hover interactions combine three subtle effects.

- Gentle lift
- Slightly softer shadow
- Tiny brightness increase

No single effect should dominate.

The overall feeling should be one of quiet responsiveness.

---

## Press Behavior

Pressed components gently settle downward.

Shadows reduce slightly.

Scale changes remain minimal.

Interactions should resemble premium mechanical switches rather than playful animations.

---

# Motion System

## Philosophy

Motion should communicate intention rather than decoration.

Users should feel motion more than consciously notice it.

Nothing should teleport.

Everything should arrive naturally.

---

## Motion Language

Each interaction follows a consistent verb.

Buttons

Respond

Cards

Lift

Dropdowns

Unfold

Dialogs

Arrive

Notifications

Glide

Messages

Emerge

Sidebar

Reveal

Uploads

Settle

These verbs guide future animation design.

---

## Timing System

Instant

100ms

Small UI feedback.

---

Quick

180ms

Hover

Focus

Buttons

Most common interaction.

---

Comfortable

280ms

Dropdowns

Sidebar

Cards

Uploads

---

Expressive

400ms

Landing page

Major transitions

Rare moments.

---

## Easing

Linear animation should never be used.

Motion should accelerate and decelerate naturally, resembling physical objects.

---

## AI Thinking

Loading indicators should never rely on spinning animations.

Instead, the interface should quietly breathe.

The experience should communicate calm intelligence rather than waiting.

---

## Streaming

Responses should feel like thoughts gradually becoming words.

Streaming should remain smooth and natural.

---

## Digital Craftsmanship

Every animation should answer one question:

"What physical behavior is this imitating?"

Examples:

Button

Mechanical switch

Dropdown

Folder unfolding

Upload

Document settling

Dialog

Paper placed onto a desk

The objective is to recreate physical craftsmanship digitally.

---

## Organic Intelligence

Vellichor introduces a second motion principle.

The interface should never feel static.

Instead, it should possess a subtle sense of life.

Examples include:

- Ambient breathing
- Gentle lighting shifts
- Calm AI pulse
- Quiet workspace awareness

The application should feel present without becoming distracting.

---

# Iconography

Vellichor uses:

Lucide Icons

Reasons:

- Modern
- Minimal
- Consistent
- Open source
- Elegant stroke style

Outlined icons should be preferred over filled icons.

Icons should support text rather than replace it.

---

# Component Tokens

Every component inherits the same visual language.

Buttons

Soft premium corners.

Crafted hover feedback.

Gentle motion.

---

Inputs

Comfortable sizing.

Warm focus states.

Calm interaction.

---

Cards

Matte surfaces.

Comfortable spacing.

Minimal shadows.

---

Chat Bubbles

Elegant conversation cards.

Reading-first layout.

High readability.

---

Sidebar

Quiet organization.

Modern workspace.

No unnecessary decoration.

---

Upload Area

Uploading should feel like placing a valuable document into a carefully organized workspace.

---

Dialogs

Arrive naturally.

Never pop abruptly.

---

Dropdowns

Unfold gracefully.

Never simply appear.

---

Toasts

Reassure.

Never interrupt.

---

# Accessibility

Vellichor considers accessibility a core quality feature.

Requirements include:

- High contrast typography
- Visible keyboard focus
- Reduced motion support
- Comfortable reading sizes
- Clear interaction states
- Never relying solely on color to communicate meaning

Accessibility should feel naturally integrated rather than added afterward.

---

# Design Rules

Every new interface element should satisfy these principles.

- Craftsmanship over decoration.
- Calm over excitement.
- Comfort over density.
- Hierarchy over color.
- Motion over animation.
- Intention over novelty.
- Timelessness over trends.
- Consistency over experimentation.

---

# Guiding Question

Whenever a new component is created, ask:

> "Does this interaction quietly reward the user through thoughtful craftsmanship?"

If the answer is no, the design should be refined.

---

# Summary

The Vellichor Design System establishes a consistent visual language built upon calmness, timeless elegance, digital craftsmanship, and reading comfort.

Rather than relying on visual trends, it emphasizes thoughtful restraint, subtle interaction, and exceptional attention to detail.

Every future component, animation, layout, and feature should inherit these principles to ensure the entire application feels cohesive, refined, and unmistakably Vellichor.