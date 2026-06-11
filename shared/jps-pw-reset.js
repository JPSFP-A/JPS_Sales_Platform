/* JPS shared password reset — OTP 6-digit code flow.
   Defeats M365 SafeLinks one-time-token burn (scanners can't "click" a code).
   Self-contained: injects a "Forgot password?" link + its own modal (own styles).
   Per-app init (after login markup exists):
     JpsPwReset.init({ getClient: function(){ return getSB(); },
                       anchorSelector: '#lBtn', emailInputId: 'lEmail' });
   getClient must return a Supabase-js v2 client.
   NOTE: requires Supabase "Reset Password" email template to include {{ .Token }}
   and a working SMTP for the code email to actually arrive. */
(function () {
  var C = {};
  function $(id) { return document.getElementById(id); }
  var LBL = 'display:block;font-size:9.5px;font-weight:700;color:rgba(255,255,255,.5);letter-spacing:.07em;text-transform:uppercase;margin:0 0 5px';
  var INP = 'width:100%;padding:10px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.08);color:#fff;font-size:13px;outline:none;box-sizing:border-box;font-family:inherit';
  var BTN = 'width:100%;margin-top:12px;padding:11px;border:none;border-radius:9px;cursor:pointer;background:linear-gradient(135deg,#003da5,#00aeef);color:#fff;font-size:13px;font-weight:700';

  function buildModal() {
    if ($('jpr-ov')) return;
    var ov = document.createElement('div');
    ov.id = 'jpr-ov';
    ov.style.cssText = 'position:fixed;inset:0;z-index:2147483000;display:none;align-items:center;justify-content:center;background:rgba(2,8,20,.72)';
    ov.innerHTML =
      '<div role="dialog" aria-modal="true" style="width:330px;max-width:92vw;background:#0b1730;border:1px solid rgba(0,174,239,.28);border-radius:14px;padding:22px;box-shadow:0 24px 70px rgba(0,0,0,.6);font-family:system-ui,-apple-system,Segoe UI,sans-serif">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px">'
      +   '<div style="font-size:15px;font-weight:800;color:#fff">Reset password</div>'
      +   '<div id="jpr-x" role="button" aria-label="Close" style="cursor:pointer;font-size:20px;color:rgba(255,255,255,.5);line-height:1">&times;</div>'
      + '</div>'
      + '<div id="jpr-s1">'
      +   '<label style="' + LBL + '">Email</label>'
      +   '<input id="jpr-email" type="email" autocomplete="username" placeholder="you@jpsco.com" style="' + INP + '">'
      +   '<button id="jpr-send" type="button" style="' + BTN + '">Send reset code</button>'
      + '</div>'
      + '<div id="jpr-s2" style="display:none">'
      +   '<label style="' + LBL + '">6-digit code (from email)</label>'
      +   '<input id="jpr-code" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="123456" style="' + INP + '">'
      +   '<label style="' + LBL + ';margin-top:11px">New password (min 8)</label>'
      +   '<input id="jpr-new" type="password" autocomplete="new-password" placeholder="new password" style="' + INP + '">'
      +   '<button id="jpr-confirm" type="button" style="' + BTN + '">Set password &amp; sign in</button>'
      + '</div>'
      + '<div id="jpr-msg" style="font-size:11px;text-align:center;margin-top:11px;min-height:14px;font-weight:600;color:#ff8a8a"></div>'
      + '</div>';
    document.body.appendChild(ov);
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    $('jpr-x').onclick = close;
    $('jpr-send').onclick = sendCode;
    $('jpr-confirm').onclick = confirmReset;
  }

  function msg(t, ok) { var m = $('jpr-msg'); if (m) { m.textContent = t || ''; m.style.color = ok ? '#7CFCB4' : '#ff8a8a'; } }

  function open() {
    buildModal();
    $('jpr-s2').style.display = 'none';
    $('jpr-code').value = ''; $('jpr-new').value = ''; msg('');
    var pre = C.emailInputId && $(C.emailInputId) ? $(C.emailInputId).value.trim() : '';
    if (pre) $('jpr-email').value = pre;
    $('jpr-ov').style.display = 'flex';
    setTimeout(function () { try { $('jpr-email').focus(); } catch (e) {} }, 30);
  }
  function close() { var o = $('jpr-ov'); if (o) o.style.display = 'none'; }

  function client() {
    try { return C.getClient ? C.getClient() : (window.getSB ? window.getSB() : null); }
    catch (e) { return null; }
  }

  async function sendCode() {
    var email = $('jpr-email').value.trim();
    if (!email) { msg('Enter your email.'); return; }
    var b = $('jpr-send'); b.disabled = true; b.textContent = 'Sending…';
    try {
      var sb = client(); if (!sb) throw new Error('Auth client unavailable');
      var r = await sb.auth.resetPasswordForEmail(email);
      if (r.error) throw r.error;
      $('jpr-s2').style.display = 'block';
      msg('If that email is registered, a 6-digit code was sent. Check inbox & spam.', true);
      $('jpr-code').focus();
    } catch (e) { msg((e && e.message) || 'Could not send reset code.'); }
    finally { b.disabled = false; b.textContent = 'Resend code'; }
  }

  async function confirmReset() {
    var email = $('jpr-email').value.trim(), code = $('jpr-code').value.trim(), np = $('jpr-new').value;
    if (!code || code.length < 6) { msg('Enter the 6-digit code.'); return; }
    if (!np || np.length < 8) { msg('New password must be at least 8 characters.'); return; }
    var b = $('jpr-confirm'); b.disabled = true; b.textContent = 'Verifying…';
    try {
      var sb = client(); if (!sb) throw new Error('Auth client unavailable');
      var v = await sb.auth.verifyOtp({ email: email, token: code, type: 'recovery' });
      if (v.error) throw v.error;
      var u = await sb.auth.updateUser({ password: np });
      if (u.error) throw u.error;
      msg('Password updated. You can now sign in with your new password.', true);
      // scope:'global' revokes ALL of this user's sessions (old tokens die) — reset = full re-auth
      try { await sb.auth.signOut({ scope: 'global' }); } catch (_) {}
      setTimeout(function () {
        close();
        if (C.emailInputId && $(C.emailInputId)) $(C.emailInputId).value = email;
      }, 1500);
    } catch (e) {
      msg((e && e.message) || 'Reset failed — the code may be wrong or expired.');
      b.disabled = false; b.textContent = 'Set password & sign in';
    }
  }

  function injectLink() {
    if (document.getElementById('jpr-link')) return;
    var anchor = C.anchorSelector ? document.querySelector(C.anchorSelector) : null;
    if (!anchor) return;
    var wrap = document.createElement('div');
    wrap.style.cssText = 'text-align:center;margin-top:11px';
    wrap.innerHTML = '<a id="jpr-link" href="#" style="color:#00aeef;font-size:11px;font-weight:600;text-decoration:none;cursor:pointer">Forgot password?</a>';
    anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
    document.getElementById('jpr-link').addEventListener('click', function (e) { e.preventDefault(); open(); });
  }

  window.JpsPwReset = {
    init: function (cfg) {
      C = cfg || {};
      function go() { try { injectLink(); buildModal(); } catch (e) {} }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go);
      else go();
    },
    open: open
  };
})();
