// Contact form on contact.html. Posts to the pf-contact Worker
// (forms.pandafederation.com). Email support@pandafederation.com still works.
(function () {
  var form = document.getElementById("contact-form");
  if (!form || !window.fetch) return;
  var API = "https://forms.pandafederation.com";
  var status = form.querySelector(".form-status");
  var button = form.querySelector('button[type="submit"]');
  var tokenField = form.querySelector('input[name="token"]');

  // Spam trap for bots: a field people never see or fill in.
  var trap = document.createElement("input");
  trap.type = "text"; trap.name = "website"; trap.tabIndex = -1;
  trap.autocomplete = "off"; trap.setAttribute("aria-hidden", "true");
  trap.className = "cf-trap";
  form.appendChild(trap);

  function say(msg, bad) {
    status.textContent = msg;
    status.className = "form-status" + (bad ? " bad" : " ok");
  }
  function getToken() {
    return fetch(API + "/token", { credentials: "omit" })
      .then(function (r) { if (!r.ok) throw new Error("token"); return r.json(); })
      .then(function (j) { tokenField.value = j.token || ""; });
  }
  getToken().catch(function () {
    say("The form is unavailable right now. Please email support@pandafederation.com.", true);
  });

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (!tokenField.value) { say("Please wait a moment and try again, or email support@pandafederation.com.", true); getToken().catch(function () {}); return; }
    button.disabled = true;
    say("Sending…", false);
    fetch(API + "/contact", {
      method: "POST", body: new FormData(form), credentials: "omit",
      headers: { Accept: "application/json" }
    })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j.ok) {
          form.reset();
          say("Thanks. We got your message and will reply by email within 1 business day. We do not send an automatic copy of this form to you.", false);
        } else {
          var extra = j.errors ? " " + Object.keys(j.errors).map(function (k) { return j.errors[k]; }).join(" ") : "";
          say((j.error || "Something went wrong. Please email support@pandafederation.com.") + extra, true);
        }
      })
      .catch(function () { say("We could not send that. Please email support@pandafederation.com.", true); })
      .then(function () { button.disabled = false; tokenField.value = ""; getToken().catch(function () {}); });
  });
})();
