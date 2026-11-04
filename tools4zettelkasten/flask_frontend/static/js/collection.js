/* collection.js
 * Copyright (c) 2026 Dr. Rupert Rebentisch
 * Licensed under the MIT license
 *
 * Holds the collection of notes selected for export. The collection lives in
 * localStorage, so it needs no server state, survives restarts and also works
 * when the web UI runs in read-only mode.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 't4z_collection';

  /* Read the collection. Corrupt content is treated as an empty collection. */
  function items() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return [];
      }
      var parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) {
        return [];
      }
      return parsed.filter(function (entry) {
        return typeof entry === 'string' && entry.length > 0;
      });
    } catch (error) {
      return [];
    }
  }

  function store(list) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (error) {
      /* Storage unavailable (private mode, quota): keep the page working. */
    }
    render();
  }

  function has(filename) {
    return items().indexOf(filename) !== -1;
  }

  function add(filename) {
    var list = items();
    if (list.indexOf(filename) === -1) {
      list.push(filename);
      store(list);
    }
  }

  function addAll(filenames) {
    var list = items();
    filenames.forEach(function (filename) {
      if (list.indexOf(filename) === -1) {
        list.push(filename);
      }
    });
    store(list);
  }

  function remove(filename) {
    store(items().filter(function (entry) {
      return entry !== filename;
    }));
  }

  function toggle(filename) {
    if (has(filename)) {
      remove(filename);
    } else {
      add(filename);
    }
  }

  function move(filename, delta) {
    var list = items();
    var from = list.indexOf(filename);
    var to = from + delta;
    if (from === -1 || to < 0 || to >= list.length) {
      return;
    }
    list.splice(to, 0, list.splice(from, 1)[0]);
    store(list);
  }

  function clear() {
    store([]);
  }

  /* Derive a readable title from a filename, like title_from_filename()
   * does on the server: strip the id, strip the ordering, unescape the
   * underscores. */
  function titleFromFilename(filename) {
    var name = filename.replace(/\.md$/, '');
    name = name.replace(/_[0-9a-f]{9}$/, '');
    if (/^[0-9]/.test(name)) {
      var match = /_[^0-9]/.exec(name);
      if (match) {
        name = name.slice(match.index + 1);
      }
    }
    return name.replace(/_/g, ' ');
  }

  /* Collect a note together with all of its descendants, in the
   * hierarchical order of the list view. The descendants of a note are the
   * following rows whose ordering extends its ordering. */
  function subtreeOf(filename) {
    var rows = Array.prototype.slice.call(
      document.querySelectorAll('[data-filename][data-ordering]'));
    var start = -1;
    var ordering = '';
    rows.forEach(function (row, index) {
      if (start === -1 && row.getAttribute('data-filename') === filename) {
        start = index;
        ordering = row.getAttribute('data-ordering');
      }
    });
    if (start === -1) {
      return [filename];
    }
    var collected = [filename];
    if (!ordering) {
      return collected;
    }
    for (var index = start + 1; index < rows.length; index += 1) {
      var candidate = rows[index].getAttribute('data-ordering') || '';
      if (candidate.indexOf(ordering + '_') !== 0) {
        break;
      }
      collected.push(rows[index].getAttribute('data-filename'));
    }
    return collected;
  }

  /* Keep counters, toggle buttons and the collection list in sync. */
  function render() {
    var list = items();

    Array.prototype.forEach.call(
      document.querySelectorAll('[data-collection-count]'),
      function (element) {
        element.textContent = String(list.length);
      });

    Array.prototype.forEach.call(
      document.querySelectorAll('[data-collection-toggle]'),
      function (button) {
        var filename = button.getAttribute('data-filename');
        var inCollection = list.indexOf(filename) !== -1;
        button.classList.toggle('btn-success', inCollection);
        button.classList.toggle('btn-outline-primary', !inCollection);
        button.setAttribute('aria-pressed', String(inCollection));
        var labels = button.getAttribute('data-labels');
        if (labels) {
          var parts = labels.split('|');
          button.textContent = inCollection ? parts[1] : parts[0];
        }
      });

    renderCollectionPage(list);
  }

  function renderCollectionPage(list) {
    var container = document.getElementById('collection-entries');
    if (!container) {
      return;
    }
    var empty = document.getElementById('collection-empty');
    var controls = document.getElementById('collection-controls');
    if (empty) {
      empty.hidden = list.length > 0;
    }
    if (controls) {
      controls.hidden = list.length === 0;
    }

    container.innerHTML = '';
    list.forEach(function (filename, index) {
      var row = document.createElement('tr');

      var position = document.createElement('th');
      position.scope = 'row';
      position.textContent = String(index + 1);
      row.appendChild(position);

      var titleCell = document.createElement('td');
      var link = document.createElement('a');
      link.href = '/' + filename;
      link.textContent = titleFromFilename(filename);
      titleCell.appendChild(link);
      var source = document.createElement('div');
      source.className = 'text-muted small';
      source.textContent = filename;
      titleCell.appendChild(source);
      row.appendChild(titleCell);

      var actions = document.createElement('td');
      actions.className = 'text-nowrap';
      actions.appendChild(actionButton('↑', 'Move up', function () {
        move(filename, -1);
      }, index === 0));
      actions.appendChild(actionButton('↓', 'Move down', function () {
        move(filename, 1);
      }, index === list.length - 1));
      actions.appendChild(actionButton('✕', 'Remove', function () {
        remove(filename);
      }, false));
      row.appendChild(actions);

      container.appendChild(row);
    });
  }

  function actionButton(label, title, handler, disabled) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-sm btn-outline-secondary me-1';
    button.textContent = label;
    button.title = title;
    button.setAttribute('aria-label', title);
    button.disabled = Boolean(disabled);
    button.addEventListener('click', handler);
    return button;
  }

  /* Write the collection into the export form, in order, right before it is
   * submitted. */
  function prepareExportForm(form) {
    var target = document.getElementById('collection-files');
    if (!target) {
      return;
    }
    target.innerHTML = '';
    items().forEach(function (filename) {
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'files';
      input.value = filename;
      target.appendChild(input);
    });
  }

  function wire() {
    Array.prototype.forEach.call(
      document.querySelectorAll('[data-collection-toggle]'),
      function (button) {
        button.addEventListener('click', function () {
          toggle(button.getAttribute('data-filename'));
        });
      });

    Array.prototype.forEach.call(
      document.querySelectorAll('[data-collection-subtree]'),
      function (button) {
        button.addEventListener('click', function () {
          addAll(subtreeOf(button.getAttribute('data-filename')));
        });
      });

    Array.prototype.forEach.call(
      document.querySelectorAll('[data-collection-clear]'),
      function (button) {
        button.addEventListener('click', function () {
          clear();
        });
      });

    var form = document.getElementById('collection-form');
    if (form) {
      form.addEventListener('submit', function () {
        prepareExportForm(form);
      });
    }

    render();
  }

  window.t4zCollection = {
    items: items,
    has: has,
    add: add,
    addAll: addAll,
    remove: remove,
    toggle: toggle,
    move: move,
    clear: clear,
    subtreeOf: subtreeOf,
    titleFromFilename: titleFromFilename,
    render: render
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
}());
