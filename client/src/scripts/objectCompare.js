export default function compare(a, b) {
  if (a.value !== b.value) {
    return false;
  }

  if (a.sourceId !== b.sourceId) {
    return false;
  }

  if ((!a.children && b.children) || (a.children && !b.children)) {
    return false;
  }

  if (a.children && b.children) {
    if (a.children.length !== b.children.length) {
      return false;
    }

    for (const i in a.children) {
      if (!compare(a.children[i], b.children[i])) {
        return false;
      }
    }
  }

  return true;
}
