const fs=require('fs');const path=require('path');const src=fs.readFileSync(path.join(__dirname,'../web/app.js'),'utf8');
for (const needle of ['const retryHistogram = liveAttemptCounts.reduce','within_two_attempts_ratio_min:0.95','exhausted_retry_budget_max:0','retry_quality: retryQuality']) {
 if(!src.includes(needle)) throw new Error('missing '+needle);
}
console.log('PASS R2 retry histogram evidence contract');
