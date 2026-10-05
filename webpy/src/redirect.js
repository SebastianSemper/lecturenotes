    const target = new URL("dsv/", window.location.href);
    target.search = window.location.search;
    target.hash = window.location.hash;
    document.getElementById("dsv-link").href = target.href;
    window.location.replace(target.href);
