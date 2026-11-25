// Overrides the Quartz submodule's own quartz.layout.ts. The deploy workflow
// copies docs/* into sites/docs/ before building, so this file lands next to
// Quartz's sources and its relative imports resolve there, not here.
//
// Two changes from upstream: the Explorer gets a sortFn, so pages can set an
// `order:` number in their frontmatter to control sidebar position, and the
// footer links to this repository instead of Quartz's own repo and Discord.
// Everything else is upstream's default layout, kept verbatim so that bumping
// the Quartz submodule is a small diff to review rather than a rewrite.
//
// Customizing the explorer through sortFn is Quartz's documented extension
// point: https://quartz.jzhao.xyz/features/explorer

import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { FileNode } from "./quartz/components/ExplorerNode"

/**
 * Sidebar order.
 *
 * Quartz sorts folders first, then alphabetically. That is wrong for a section
 * meant to be read in sequence — "Start Here" would land fifth of six in
 * Development. Pages opt into an explicit position with frontmatter:
 *
 *     ---
 *     order: 1
 *     ---
 *
 * Lower numbers come first. Pages without `order` keep Quartz's default
 * behaviour and sort alphabetically *after* the ordered ones, so adding a page
 * without touching this file degrades gracefully instead of silently jumping to
 * the top of the section. (Quartz's own documented nameOrderMap example has the
 * opposite failure mode: unlisted entries sort first.)
 */
function explorerOrder(node: FileNode): number | undefined {
  const order = node.file?.frontmatter?.order
  return typeof order === "number" ? order : undefined
}

function sortByFrontmatterOrder(a: FileNode, b: FileNode): number {
  const orderA = explorerOrder(a)
  const orderB = explorerOrder(b)

  if (orderA !== undefined && orderB !== undefined) {
    if (orderA !== orderB) return orderA - orderB
  } else if (orderA !== undefined) {
    return -1
  } else if (orderB !== undefined) {
    return 1
  }

  // Upstream default: folders first, then files, each alphabetically.
  if ((!a.file && !b.file) || (a.file && b.file)) {
    return a.displayName.localeCompare(b.displayName, undefined, {
      numeric: true,
      sensitivity: "base",
    })
  }
  return a.file && !b.file ? 1 : -1
}

// Passed to each Explorer instance; upstream constructs one per layout.
const explorerOptions = { sortFn: sortByFrontmatterOrder }

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/bkorzh/dbay",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.DesktopOnly(Component.Explorer(explorerOptions)),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.DesktopOnly(Component.Explorer(explorerOptions)),
  ],
  right: [],
}
