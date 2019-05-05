import '../scss/main.scss';
import("./startup.js")
  .catch(e => console.error("Error importing `startup.js`:", e));
