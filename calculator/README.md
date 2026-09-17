# Interactive Calculator Proof

A browser-native calculator used to verify the full path from UI input to observable result.

The page uses real `<button>` elements and a delegated `click` listener. Arithmetic is parsed without `eval()` or `Function()`.

Expected manual proof: open the page in a normal browser, tap `2`, `+`, `2`, `=`, and observe `4`.
