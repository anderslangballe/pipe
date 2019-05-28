export default function colorFromStr(str) {
    for (var i = 0, hash = 0; i < str.length; hash = str.charCodeAt(i++) + ((hash << 5) - hash));
    const color = Math.floor(Math.abs((Math.sin(hash) * 69) % 1 * 16777216)).toString(16);
    return `#${Array(6 - color.length + 1).join('0') + color}`;
}
