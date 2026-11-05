/* =========================================================================
   flow-walkthrough.js — harness for driving a multi-state HTML artifact with
   REAL clicks and asserting every transition.

   Copy this whole file into a browser_exec `js(...)` call after opening the
   artifact, and edit CONFIG + STEPS. It returns a log of ok/FAIL lines.

   Python side, one call:

     url = "file:///C:/path/to/artifact.html"
     goto_url(url); wait_for_load()          # reload before EVERY scenario:
                                             # page state survives between
                                             # js() calls on the same page
     print(js(WALKTHROUGH))                  # the string above
     print(capture_screenshot())

   What is baked in, and why:
   - every lookup is scoped to the currently visible view, so a control on a
     hidden view cannot be clicked by accident (the classic false FAIL)
   - one line per step: ok/FAIL against the expected view name
   - text snapshots are taken from the visible view only
   - a real overflow check, because a screenshot can look fine while the page
     scrolls sideways
   ========================================================================= */
const WALKTHROUGH = String.raw`
(() => {
  // ---- CONFIG: how this artifact marks the view that is on screen ---------
  const CONFIG = {
    views:    '.screen',      // selector matching every view
    active:   'is-active',    // class present on the visible one (or use attr)
    id:       'data-screen',  // attribute holding the view's name
    text:     '.title, p',    // what to snapshot as this view's content
    controls: 'button, [role="button"], a[href]'
  };

  // ---- STEPS: edit from here down ----------------------------------------
  // desc   : label printed with the result
  // click  : control label to click (matched inside the visible view)
  // nth    : index of the control to click instead of matching by label
  // expect : the view name that should be showing after this step
  const STEPS = [
    { desc: 'lands on the start view',                       expect: '1' },
    { desc: 'Welcome -> intro',        click: 'Welcome',     expect: '2' },
    { desc: 'Continue -> next',        click: 'Continue',    expect: '3' },
    { desc: 'open the first item',     nth: 0,               expect: '3a' },
    { desc: 'Back -> returns to the row',  click: 'Back',    expect: '3' },
    { desc: 'Back -> intro',               click: 'Back',    expect: '2' },
    { desc: 'Back on the start view holds still', click: 'Back', expect: '2' }
  ];

  // ---- harness: leave alone ----------------------------------------------
  const log = [];
  const views  = () => [...document.querySelectorAll(CONFIG.views)];
  const active = () => views().find(v => v.classList.contains(CONFIG.active));
  const here   = () => { const a = active(); return a ? a.getAttribute(CONFIG.id) : 'NONE'; };
  const inView = (sel) => [...active().querySelectorAll(sel)];
  const control = (label) => inView(CONFIG.controls).find(
      c => c.textContent.trim() === label && !c.disabled);

  const snapshot = () => inView(CONFIG.text).map(e => e.textContent.trim())
      .filter(Boolean).join(' | ').slice(0, 400);

  STEPS.forEach((s, i) => {
    if (s.click !== undefined || s.nth !== undefined) {
      let c;
      if (s.nth !== undefined) c = inView(CONFIG.controls)[s.nth];
      else c = control(s.click);
      if (!c) { log.push('FAIL ' + (i + 1) + ' ' + s.desc +
                        ' -> no control "' + (s.click || s.nth) + '" on view ' + here());
                return; }
      c.click();
    }
    const got = here();
    const ok = s.expect === undefined || got === s.expect;
    log.push((ok ? 'ok   ' : 'FAIL ') + (i + 1) + '. ' + s.desc + ' -> ' + got +
             (ok ? '' : ' (expected ' + s.expect + ')'));
    if (s.expect !== undefined) log.push('       text: ' + snapshot());
  });

  // disabled / gated controls on the final view, without enabling anything
  log.push('disabled controls here: ' + inView(CONFIG.controls)
      .filter(c => c.disabled).map(c => '"' + c.textContent.trim() + '"').join(', ') || 'none');

  // real horizontal overflow, which screenshots do not reveal
  const d = document.documentElement;
  log.push('overflow: scrollWidth ' + d.scrollWidth + ' vs clientWidth ' + d.clientWidth +
           (d.scrollWidth > d.clientWidth ? '  <-- SCROLLS SIDEWAYS' : '  (clean)'));

  return log.join('\n');
})()
`;
