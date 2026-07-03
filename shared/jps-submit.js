/* jps-submit.js — shared "Submit to Finance" action for JPS satellite apps.
 * Adds a floating button + modal that posts a budget_submissions row into the
 * platform Commit Inbox. Self-contained: loads its own version/period ref data.
 *
 * Usage (after the app's authenticated Supabase client exists):
 *   <script src="shared/jps-submit.js"></script>
 *   JpsSubmit.mount(sb, { sourceApp: 'om' });
 *   // optional line-level payload:  { sourceApp:'om', getLines: () => [{line_id, value}] }
 *
 * Requires: budget_submissions + budget_submission_events (phase1/001). No innerHTML; logged catches.
 */
(function (root) {
  'use strict';

  function el(tag, css, text) {
    var n = document.createElement(tag);
    if (css) n.style.cssText = css;
    if (text != null) n.textContent = text;
    return n;
  }
  var INPUT = 'width:100%;padding:9px;margin-bottom:10px;border-radius:6px;border:1px solid #1e4a7a;' +
              'background:#0d1e3a;color:#e2f0fb;box-sizing:border-box;font:inherit;';

  function toast(msg, bad) {
    var t = el('div',
      'position:fixed;bottom:74px;right:20px;z-index:2147483646;max-width:320px;padding:11px 14px;' +
      'border-radius:8px;font:13px system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.4);' +
      'background:#132847;border:1px solid ' + (bad ? '#ef444455;color:#f87171' : '#00aeef55;color:#cfe3f5'), msg);
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 3500);
  }

  async function loadOptions(sb, selVer, selPer) {
    try {
      var v = await sb.from('fpa_versions').select('id,code,name')
        .eq('is_locked', false).order('created_at', { ascending: false }).limit(50);
      (v.data || []).forEach(function (r) {
        var o = el('option', '', r.code + ' — ' + r.name); o.value = r.id; selVer.appendChild(o);
      });
    } catch (e) { console.error('[jps-submit] versions load', e); }
    try {
      var p = await sb.from('fpa_dim_period').select('id,ym_label')
        .eq('is_closed', false).order('id', { ascending: false }).limit(36);
      (p.data || []).forEach(function (r) {
        var o = el('option', '', r.ym_label); o.value = r.id; selPer.appendChild(o);
      });
    } catch (e) { console.error('[jps-submit] periods load', e); }
  }

  function openModal(sb, sourceApp, opts) {
    if (document.getElementById('_jpsSubmitOv')) return;
    var ov = el('div', 'position:fixed;inset:0;z-index:2147483645;background:rgba(5,12,24,.7);' +
      'display:flex;align-items:center;justify-content:center;font:14px system-ui,sans-serif;');
    ov.id = '_jpsSubmitOv';
    var card = el('div', 'background:#132847;border:1px solid #1e4a7a;border-radius:12px;padding:24px;' +
      'width:380px;max-width:92vw;color:#e2f0fb;');
    card.appendChild(el('div', 'font-weight:700;font-size:15px;margin-bottom:2px;', 'Submit to Finance'));
    card.appendChild(el('div', 'font-size:12px;color:#7ba4c4;margin-bottom:16px;',
      sourceApp.toUpperCase() + ' → platform Commit Inbox'));

    card.appendChild(el('label', 'font-size:11px;color:#7ba4c4;', 'Version'));
    var selVer = el('select', INPUT); selVer.appendChild(el('option', '', 'Select version…'));
    card.appendChild(selVer);
    card.appendChild(el('label', 'font-size:11px;color:#7ba4c4;', 'Period'));
    var selPer = el('select', INPUT); selPer.appendChild(el('option', '', 'Select period…'));
    card.appendChild(selPer);
    card.appendChild(el('label', 'font-size:11px;color:#7ba4c4;', 'Note (optional)'));
    var note = el('textarea', INPUT + 'height:64px;resize:vertical;');
    card.appendChild(note);

    var err = el('div', 'color:#f87171;font-size:12px;min-height:14px;margin-bottom:8px;');
    card.appendChild(err);

    var rowBtns = el('div', 'display:flex;gap:8px;justify-content:flex-end;');
    var cancel = el('button', 'padding:9px 14px;border-radius:6px;border:1px solid #1e4a7a;background:transparent;' +
      'color:#cfe3f5;font:inherit;cursor:pointer;', 'Cancel');
    var send = el('button', 'padding:9px 16px;border-radius:6px;border:none;background:#00aeef;color:#0d1e3a;' +
      'font-weight:700;font:inherit;cursor:pointer;', 'Submit');
    rowBtns.appendChild(cancel); rowBtns.appendChild(send); card.appendChild(rowBtns);
    ov.appendChild(card); document.body.appendChild(ov);

    cancel.addEventListener('click', function () { ov.remove(); });
    loadOptions(sb, selVer, selPer);

    send.addEventListener('click', async function () {
      err.textContent = '';
      if (!selVer.value || !selPer.value) { err.textContent = 'Pick a version and period.'; return; }
      send.disabled = true; send.textContent = 'Submitting…';
      var lines = [];
      try { if (typeof opts.getLines === 'function') lines = opts.getLines() || []; }
      catch (e) { console.error('[jps-submit] getLines', e); }

      var verLabel = selVer.options[selVer.selectedIndex].textContent.split(' — ')[0];
      var perLabel = selPer.options[selPer.selectedIndex].textContent;
      var uid = null;
      try { var u = await sb.auth.getUser(); uid = u && u.data && u.data.user ? u.data.user.id : null; }
      catch (e) { console.error('[jps-submit] getUser', e); }

      var ins;
      try {
        ins = await sb.from('budget_submissions').insert({
          source_app: sourceApp,
          version_id: selVer.value,                 // fpa_versions.id (uuid)
          period_id: String(selPer.value),
          title: sourceApp.toUpperCase() + ' ' + verLabel + ' — ' + perLabel,
          status: 'submitted',
          payload: { note: note.value || '', lines: lines, source: 'app' },
          submitted_by: uid, submitted_at: new Date().toISOString(),
        }).select('id').single();
      } catch (e) { console.error('[jps-submit] insert', e); err.textContent = 'Submit failed.'; send.disabled = false; send.textContent = 'Submit'; return; }

      if (ins.error) {
        err.textContent = /does not exist/i.test(ins.error.message) ? 'Commit workflow not enabled yet.' : ins.error.message;
        send.disabled = false; send.textContent = 'Submit'; return;
      }
      try {
        await sb.from('budget_submission_events').insert({ submission_id: ins.data.id, to_status: 'submitted', actor: uid });
      } catch (e) { console.error('[jps-submit] event', e); }
      ov.remove();
      toast('Submitted to Finance — ' + (lines.length ? lines.length + ' lines' : 'for review'));
    });
  }

  var JpsSubmit = {
    mount: function (sb, opts) {
      opts = opts || {};
      if (document.getElementById('_jpsSubmitBtn')) return;
      var btn = el('button',
        'position:fixed;bottom:20px;right:20px;z-index:2147483644;padding:11px 16px;border-radius:24px;' +
        'border:none;background:#00aeef;color:#0d1e3a;font:600 13px system-ui,sans-serif;cursor:pointer;' +
        'box-shadow:0 6px 18px rgba(0,0,0,.35);', opts.label || 'Submit to Finance');
      btn.id = '_jpsSubmitBtn';
      btn.addEventListener('click', function () { openModal(sb, opts.sourceApp || 'unknown', opts); });
      document.body.appendChild(btn);
    },
    open: openModal,
  };

  root.JpsSubmit = JpsSubmit;
})(window);
