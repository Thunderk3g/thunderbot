// Used by test_setup_keys.py to check that the dashboard's encryption (dashboard/lib/secrets.ts) and the
// worker's (thunderbot/secrets.py) read each other's output. Run as:
//   node --conditions=react-server --experimental-strip-types secrets_vector.mjs <secrets.ts> <master> <blob-from-python>
// Prints one JSON line: {"fromPython": <decrypted object>, "blob": <a fresh ciphertext of the same object>}.
const [, , modulePath, master, blob] = process.argv;
const { encryptSecret, decryptSecret } = await import(modulePath);
const fromPython = decryptSecret(blob, master);
console.log(JSON.stringify({ fromPython, blob: encryptSecret(fromPython, master) }));
