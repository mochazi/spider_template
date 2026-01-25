var K = function(e) {
    for (var t, o = e.toString(), i = [], r = 0; r < o.length; r++)
        0 <= (t = o.charCodeAt(r)) && t <= 127 ? i.push(t) : 128 <= t && t <= 2047 ? (i.push(192 | 31 & t >> 6),
        i.push(128 | 63 & t)) : (2048 <= t && t <= 55295 || 57344 <= t && t <= 65535) && (i.push(224 | 15 & t >> 12),
        i.push(128 | 63 & t >> 6),
        i.push(128 | 63 & t));
    for (var a = 0; a < i.length; a++)
        i[a] &= 255;
    return i
}

function get_t(e){
    var t = [], o = [];

    o = K(e);
    for (var i = 0, r = o.length; i < r; ++i)
        t.push((5 ^ o[i]).toString(16));

    return t.join("");
}

console.log(JSON.stringify({
    'email': get_t("python_email"),
    'password': get_t("python_password"),
}))

