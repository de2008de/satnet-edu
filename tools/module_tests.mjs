import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validateTrace} from '../web/player/dist/esm/satnet-edu-player.js';
const folder=new URL('../tests/fixtures/',import.meta.url);
let rejected=0;
for(const name of fs.readdirSync(folder).filter(n=>n.startsWith('invalid-'))){
  assert.throws(()=>validateTrace(JSON.parse(fs.readFileSync(new URL(name,folder),'utf8'))));rejected++;
}
for(const name of ['minimal-valid.json','real-engine-route.json']) validateTrace(JSON.parse(fs.readFileSync(new URL(name,folder),'utf8')));
console.log(`ESM contract: two valid files accepted, ${rejected} corrupt files rejected.`);
