(function () {
  'use strict';

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  window.qmCsrfToken = function () {
    return getCookie('csrftoken');
  };

  window.printTicketHtml = function (html) {
    var frame = document.createElement('iframe');
    frame.name = 'qm-print-frame';
    frame.style.position = 'absolute';
    frame.style.top = '-1000000px';
    document.body.appendChild(frame);
    var doc = frame.contentWindow || frame.contentDocument;
    if (doc.document) doc = doc.document;
    doc.open();
    doc.write(html);
    doc.close();
    setTimeout(function () {
      frame.contentWindow.focus();
      frame.contentWindow.print();
      document.body.removeChild(frame);
    }, 400);
  };

  window.qmPostForm = function (url, data) {
    var body = new URLSearchParams(data);
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': qmCsrfToken(),
      },
      body: body.toString(),
      credentials: 'same-origin',
    });
  };

  window.qmIssueTicket = function (url, extraData, onSuccess) {
    var data = Object.assign({ is_printed: 'True' }, extraData || {});
    qmPostForm(url, data)
      .then(function (res) { return res.text(); })
      .then(function (html) {
        printTicketHtml(html);
        if (typeof onSuccess === 'function') onSuccess();
      })
      .catch(function () {
        alert('Failed to issue ticket. Please try again.');
      });
  };

  window.qmCallQueue = function (url, boothId, rowEl) {
    if (!boothId) {
      alert('Please choose your counter / desk first.');
      return Promise.reject();
    }
    if (rowEl.classList.contains('called')) {
      var audio = rowEl.querySelector('.call-audio');
      if (audio) {
        if (audio.paused) {
          audio.currentTime = 0;
          audio.play();
        } else {
          audio.pause();
        }
      }
      return Promise.resolve();
    }
    return qmPostForm(url, { is_called: 'True', counter_booth: boothId })
      .then(function () {
        rowEl.classList.remove('bg-sky-50/50');
        rowEl.classList.add('called', 'queue-called');
      })
      .catch(function () {
        alert('Failed to call queue.');
      });
  };

  window.qmFinishQueue = function (url, rowEl) {
    return qmPostForm(url, { is_finished: 'True' })
      .then(function () {
        rowEl.classList.add('opacity-0', 'scale-95');
        setTimeout(function () { rowEl.remove(); }, 250);
      })
      .catch(function () {
        alert('Failed to finish queue.');
      });
  };

  window.qmInitTomSelect = function (selector, options) {
    if (typeof TomSelect === 'undefined') return;
    document.querySelectorAll(selector).forEach(function (el) {
      if (el.tomselect) return;
      new TomSelect(el, options || {});
    });
  };

  window.qmInitAutocomplete = function (el, url, opts) {
    if (!el || el.tomselect) return;
    var minLen = (opts && opts.minLength) || 1;
    var settings = Object.assign({
      valueField: 'id',
      labelField: 'text',
      searchField: 'text',
      load: function (query, callback) {
        if (query.length < minLen) return callback();
        fetch(url + '?q=' + encodeURIComponent(query), { credentials: 'same-origin' })
          .then(function (r) { return r.json(); })
          .then(function (json) { callback(json.results || []); })
          .catch(function () { callback(); });
      },
    }, opts || {});
    delete settings.minLength;
    new TomSelect(el, settings);
  };

  window.qmInitFlatpickr = function () {
    if (typeof flatpickr === 'undefined') return;
    document.querySelectorAll('[data-flatpickr-date]').forEach(function (el) {
      flatpickr(el, { dateFormat: 'd-m-Y', allowInput: true });
    });
    document.querySelectorAll('[data-flatpickr-time]').forEach(function (el) {
      flatpickr(el, { enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true, allowInput: true });
    });
  };

  document.body.addEventListener('htmx:configRequest', function (evt) {
    evt.detail.headers['X-CSRFToken'] = qmCsrfToken();
  });

  document.addEventListener('alpine:init', function () {
    Alpine.data('qmDropdown', function (loadUrl) {
      return {
        open: false,
        loaded: false,
        loadUrl: loadUrl,
        toggle: function () {
          this.open = !this.open;
          if (this.open && !this.loaded) {
            var menu = this.$refs.menu;
            if (menu && typeof htmx !== 'undefined') {
              htmx.ajax('GET', this.loadUrl, { target: menu, swap: 'innerHTML' });
            }
            this.loaded = true;
          }
        },
        close: function () {
          this.open = false;
        },
      };
    });

    Alpine.data('qmFloatingMenu', function () {
      return {
        open: false,
        menuTop: 0,
        menuRight: 0,
        toggle: function () {
          this.open = !this.open;
          if (this.open) this.positionMenu();
        },
        close: function () {
          this.open = false;
        },
        positionMenu: function () {
          var self = this;
          this.$nextTick(function () {
            var btn = self.$refs.trigger;
            if (!btn) return;
            var rect = btn.getBoundingClientRect();
            self.menuTop = rect.bottom + 4;
            self.menuRight = window.innerWidth - rect.right;
          });
        },
        get menuStyle() {
          return 'top:' + this.menuTop + 'px;right:' + this.menuRight + 'px;';
        },
        init: function () {
          var self = this;
          var onScroll = function () {
            if (self.open) self.close();
          };
          window.addEventListener('scroll', onScroll, true);
          window.addEventListener('resize', function () {
            if (self.open) self.positionMenu();
          });
        },
      };
    });

    Alpine.data('qmTabs', function (defaultId) {
      return {
        active: localStorage.getItem('qmActiveTab') || defaultId,
        select: function (id) {
          this.active = id;
          localStorage.setItem('qmActiveTab', id);
        },
        isActive: function (id) {
          return this.active === id;
        },
      };
    });

    Alpine.data('qmCarousel', function (count, intervalMs) {
      var autoplay = intervalMs || 8000;
      var state = {
        current: 0,
        total: count,
        next: function () {
          this.current = (this.current + 1) % this.total;
        },
        prev: function () {
          this.current = (this.current - 1 + this.total) % this.total;
        },
        isSlide: function (idx) {
          return this.current === idx;
        },
        init: function () {
          var self = this;
          setInterval(function () { self.next(); }, autoplay);
        },
      };
      return state;
    });

    Alpine.data('qmSidebar', function () {
      return {
        open: true,
        toggle: function () {
          this.open = !this.open;
        },
      };
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    if (typeof lucide !== 'undefined') lucide.createIcons();

    document.querySelectorAll('[data-auto-dismiss]').forEach(function (el) {
      setTimeout(function () {
        el.classList.add('opacity-0', 'translate-y-2');
        setTimeout(function () { el.remove(); }, 300);
      }, 5000);
    });
  });

  document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (typeof Alpine !== 'undefined') Alpine.initTree(evt.detail.target);
    if (typeof lucide !== 'undefined') lucide.createIcons();
  });
})();
