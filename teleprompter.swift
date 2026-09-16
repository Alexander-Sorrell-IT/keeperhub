import Cocoa

// THEMIS teleprompter — places itself on the right half of the screen and
// FOLLOWS the demo via a state file (arg $1). Same pattern as the sentinel
// teleprompter: demo.py writes a slide index, this polls and advances.
// Diagnostics go to stderr.

let statePath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/themis_state"

let groups: [(title: String, lines: [String])] = [
  ("OPENING — THEMIS", [
    "Every DeFi service answers all callers. Every oracle returns data to anyone who asks.",
    "THEMIS doesn't. She has her own laws, she refuses what she will not serve, and she proves her own verdicts — no external verifier.",
    "One slug. One tool call. Callable by any agent in the world." ]),
  ("PHASE 1 — The Law", [
    "Five callers walk up to the integrity gate. Three signal exploit, MEV, or front-run intent.",
    "THEMIS returns nothing. No data consumed, no verdict produced, no protocol call made.",
    "That is not an access control list. It is the agent's own law — the field repels misuse by nature." ]),
  ("PHASE 2 — The Proof", [
    "M5 = F(M1, M2, M3, M4, M5). Chronicle price, Chainlink price, Aave health factor, consistency gate, verdict.",
    "These are live Sepolia values, read through KeeperHub right now — not sample numbers.",
    "Scenario B: two percent divergence. The layers don't reconcile, so M5 is never produced. The act of solving is the proof." ]),
  ("PHASE 3 — The Build", [
    "THEMIS CORE deploys live on KeeperHub. Eight nodes: Chronicle, scale, Chainlink, scale, Aave, consistency, verdict.",
    "Every one executes against Sepolia. Watch the node count — eight of eight, not one trigger and seven empty boxes.",
    "Idempotent: an existing THEMIS is re-synced in place, keeping her id and her slug. Never duplicated." ]),
  ("PHASE 4 — The Market", [
    "Listed on the KeeperHub marketplace with an input schema and an output mapping.",
    "From this moment any agent anywhere discovers her through search_workflows and calls her through one slug.",
    "No API key. No SDK. No human. No onboarding. The builder lists once — every call after that is infrastructure use." ]),
  ("PHASE 5 — The Call", [
    "This is the Agent Economy the hackathon is named for.",
    "One tool, one slug. The caller's context is the entire input language: risk tolerance, time horizon, position.",
    "An agent just bought another agent's verdict, and the verdict came back — not an execution id, the verdict." ]),
  ("PHASE 6 — The Loop", [
    "THEMIS reads the position. The Guardian branches on her verdict. The position changes. THEMIS reads the state she caused.",
    "Her output is her next input. The Reflexive Singularity, closed in code rather than in prose.",
    "The Guardian runs on a schedule, reads the same danger floor THEMIS uses, and defends or holds." ]),
  ("PHASE 7 — The Proof", [
    "Execution ids. Node-level receipts. Live oracle values on the record.",
    "Chronicle and Chainlink agreed inside one percent, so the verdict was allowed to exist.",
    "The verdict proved itself by existing. M5 = F(M1, M2, M3, M4, M5)." ]),
  ("CLOSING", [
    "One rule. One law. One primitive.",
    "Once enough agents depend on her, she is infrastructure — and the builder disappears into the build.",
    "She was there before the Olympians and will be there after.\n\ngithub.com/Alexander-Sorrell-IT/keeperhub" ]),
]

func log(_ s: String) { FileHandle.standardError.write((s + "\n").data(using: .utf8)!) }

func makeLabel(_ size: CGFloat, _ color: NSColor, _ weight: NSFont.Weight) -> NSTextField {
  let l = NSTextField(labelWithString: "")
  l.alignment = .center
  l.font = .systemFont(ofSize: size, weight: weight)
  l.textColor = color
  l.isBezeled = false; l.drawsBackground = false; l.isEditable = false; l.isSelectable = false
  l.usesSingleLineMode = false
  l.lineBreakMode = .byWordWrapping
  l.maximumNumberOfLines = 0
  l.cell?.wraps = true
  l.translatesAutoresizingMaskIntoConstraints = false
  // never force the window wider than its frame — wrap instead
  l.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
  l.setContentHuggingPriority(.defaultLow, for: .horizontal)
  return l
}

class AppD: NSObject, NSApplicationDelegate {
  var window: NSWindow!
  let header = makeLabel(30, .systemYellow, .semibold)
  let body = makeLabel(40, .white, .bold)
  let foot = makeLabel(17, NSColor(white: 0.45, alpha: 1), .regular)
  var cur = -1

  func applicationDidFinishLaunching(_ n: Notification) {
    guard let screen = NSScreen.main else { return }
    let vis = screen.visibleFrame
    let halfW = vis.width / 2.0
    let rightRect = NSRect(
      x: vis.origin.x + halfW,
      y: vis.origin.y,
      width: halfW,
      height: vis.height
    )

    let maxW = rightRect.width * 0.88
    header.preferredMaxLayoutWidth = maxW
    body.preferredMaxLayoutWidth = maxW
    foot.preferredMaxLayoutWidth = maxW

    window = NSWindow(contentRect: rightRect, styleMask: [.titled, .closable, .resizable], backing: .buffered, defer: false)
    window.title = "THEMIS — teleprompter"
    window.backgroundColor = .black
    window.isReleasedWhenClosed = false
    window.level = .floating
    window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

    let content = NSView()
    content.wantsLayer = true
    content.layer?.backgroundColor = NSColor.black.cgColor
    content.addSubview(header); content.addSubview(body); content.addSubview(foot)
    window.contentView = content
    NSLayoutConstraint.activate([
      body.centerXAnchor.constraint(equalTo: content.centerXAnchor),
      body.centerYAnchor.constraint(equalTo: content.centerYAnchor),
      body.widthAnchor.constraint(equalTo: content.widthAnchor, multiplier: 0.88),
      header.centerXAnchor.constraint(equalTo: content.centerXAnchor),
      header.bottomAnchor.constraint(equalTo: body.topAnchor, constant: -36),
      header.widthAnchor.constraint(equalTo: content.widthAnchor, multiplier: 0.88),
      foot.centerXAnchor.constraint(equalTo: content.centerXAnchor),
      foot.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -30),
    ])

    show(0)
    window.setFrame(rightRect, display: true)
    window.makeKeyAndOrderFront(nil)
    NSApp.activate(ignoringOtherApps: true)

    Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { [weak self] _ in self?.poll() }
  }

  func poll() {
    guard !statePath.isEmpty,
          let s = try? String(contentsOfFile: statePath, encoding: .utf8),
          let i = Int(s.trimmingCharacters(in: .whitespacesAndNewlines)) else { return }
    if i != cur {
      log("[teleprompter] state signal: \(cur) -> \(i)")
      show(i)
    }
  }

  func show(_ i: Int) {
    cur = i
    let g = groups[max(0, min(i, groups.count - 1))]
    header.stringValue = "▌  \(g.title)"
    let text = g.lines.joined(separator: "\n\n")
    body.stringValue = text
    foot.stringValue = "slide \(i + 1) / \(groups.count)   ·   auto-advancing with the demo"

    let len = text.count
    let fontSize: CGFloat = len > 350 ? 25 : (len > 200 ? 28 : 32)
    body.font = .systemFont(ofSize: fontSize, weight: .bold)
    log("[teleprompter] showing slide \(i + 1)/\(groups.count): \(g.title)")
  }
}

let app = NSApplication.shared
let d = AppD()
app.delegate = d
app.setActivationPolicy(.regular)
app.run()
