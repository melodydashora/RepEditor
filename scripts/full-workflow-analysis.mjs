#!/usr/bin/env node

import pg from 'pg';
import { config } from 'dotenv';

config();

const { Client } = pg;

const LAT = 33.12855399613802;
const LNG = -96.87550973624359;
const USER_ID = process.env.TEST_USER_ID || '97b62815-2fbd-4f64-9338-7744bb62ae7c';
const BASE = process.env.BASE_URL || 'http://localhost:5000';

// Helper functions
async function post(path, body) {
  const r = await fetch(`${BASE}${path}`, { 
    method: 'POST', 
    headers: { 'content-type': 'application/json' }, 
    body: JSON.stringify(body) 
  });
  const j = await r.json().catch(() => ({}));
  return { status: r.status, json: j };
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('📊 COMPLETE WORKFLOW ANALYSIS: GPS → API → DB → Models → UI');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log();

console.log('🔷 STEP 1: GPS COORDINATES FROM DEVICE');
console.log(`   📍 Latitude: ${LAT}`);
console.log(`   📍 Longitude: ${LNG}`);
console.log(`   👤 User ID: ${USER_ID}`);
console.log();

console.log('🔷 STEP 2: TRIGGER WORKFLOW - POST /api/blocks (with polling)');
console.log(`   📤 Request: {lat: ${LAT}, lng: ${LNG}, userId: "${USER_ID}"}`);
console.log(`   ℹ️  Blocks endpoint will create snapshot internally`);
console.log();

let correlationId = null;
let blocks = null;
let snapshotId = null;
let attempts = 0;
const maxAttempts = 20;

// Poll until strategy exists and blocks are ready
for (let i = 0; i < maxAttempts; i++) {
  attempts++;
  const res = await post('/api/blocks', { 
    origin: { lat: LAT, lng: LNG },
    userId: USER_ID
  });
  
  correlationId = res.json?.correlationId || correlationId;
  snapshotId = res.json?.snapshot_id || snapshotId;
  
  if (res.status === 202) { 
    console.log(`   ⏳ Attempt ${attempts}: Strategy pending, retrying in 2s...`);
    await sleep(2000);
    continue;
  }
  
  if (res.status === 200 && Array.isArray(res.json?.blocks)) { 
    blocks = res.json.blocks;
    correlationId = res.json.correlationId;
    snapshotId = res.json.snapshot_id;
    console.log(`   ✅ Blocks ready after ${attempts} attempts`);
    break;
  }
  
  if (res.status === 400) {
    console.error(`   ❌ Attempt ${attempts}: Bad request (400)`, res.json);
    process.exit(1);
  }
  
  console.log(`   ⚠️ Attempt ${attempts}: Unexpected response (status ${res.status}), retrying in 2s...`);
  await sleep(2000);
}

if (!blocks) {
  console.error('❌ Blocks never became ready after', maxAttempts, 'attempts');
  process.exit(1);
}

console.log(`   ✅ Correlation ID: ${correlationId}`);
console.log(`   ✅ Snapshot ID: ${snapshotId}`);
console.log(`   ✅ Received ${blocks.length} blocks`);
console.log();

// Validate first venue has non-zero distance/time
const firstVenue = blocks[0];
console.log('🔷 STEP 3: VALIDATE FIRST VENUE (Routes API data)');
console.log(`   📍 Name: ${firstVenue.name}`);
console.log(`   🆔 Place ID: ${firstVenue.placeId}`);
console.log(`   📏 Distance: ${firstVenue.estimated_distance_miles} mi`);
console.log(`   ⏱️  Drive Time: ${firstVenue.driveTimeMinutes} min`);
console.log(`   📡 Source: ${firstVenue.distanceSource}`);
console.log();

if (!firstVenue.estimated_distance_miles || firstVenue.estimated_distance_miles === 0) {
  console.error('❌ VALIDATION FAILED: Distance is 0 or missing!');
  process.exit(1);
}

if (!firstVenue.driveTimeMinutes || firstVenue.driveTimeMinutes === 0) {
  console.error('❌ VALIDATION FAILED: Drive time is 0 or missing!');
  process.exit(1);
}

console.log('   ✅ VALIDATION PASSED: Distance and time are non-zero');
console.log();

// Connect to database
const client = new Client({
  connectionString: process.env.DATABASE_URL
});

await client.connect();

console.log();
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('💾 DATABASE OPERATIONS & WORKFLOW TRACE');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log();

// 1. Check snapshot table
console.log('🔷 STEP 4: GEOCODING API CALL (Reverse Geocode)');
console.log('   📡 Google Geocoding API: coordinates → address + place_id');
console.log(`   📤 Input: lat=${LAT}, lng=${LNG}`);
console.log('   📥 Output: city, state, address, timezone');
console.log();

const snapshotResult = await client.query(
  'SELECT * FROM snapshots WHERE snapshot_id = $1',
  [snapshotId]
);

if (snapshotResult.rows.length > 0) {
  const snapshot = snapshotResult.rows[0];
  console.log('🔷 STEP 4B: DB WRITE → snapshots table');
  console.log('   💾 Table: snapshots');
  console.log('   ✅ Record:', {
    snapshot_id: snapshot.snapshot_id,
    city: snapshot.city,
    state: snapshot.state,
    timezone: snapshot.timezone,
    lat: snapshot.lat,
    lng: snapshot.lng,
    h3_r8: snapshot.h3_r8,
    weather: snapshot.weather
  });
  console.log();
} else {
  console.warn('⚠️ No snapshot found in database');
  console.log();
}

// 2. Check strategy table
console.log('🔷 STEP 5: CLAUDE SONNET 4.5 STRATEGIC ANALYSIS');
console.log('   🧠 Model: claude-sonnet-4-5-20250929 (Strategist)');
console.log('   📤 Input: snapshot context (GPS, weather, time, airport status)');
console.log('   📥 Output: strategy text, pro tips, earnings estimate');
console.log();

const strategyResult = await client.query(
  'SELECT * FROM strategies WHERE correlation_id = $1',
  [correlationId]
);

if (strategyResult.rows.length > 0) {
  const strategy = strategyResult.rows[0];
  console.log('🔷 STEP 5B: DB WRITE → strategies table');
  console.log('   💾 Table: strategies');
  console.log('   ✅ Record:', {
    correlation_id: strategy.correlation_id,
    strategy_length: strategy.strategy_for_now?.length || 0,
    pro_tips_count: strategy.pro_tips?.length || 0
  });
  console.log();
} else {
  console.warn('⚠️ No strategy found in database');
  console.log();
}

// 3. Check rankings table
console.log('🔷 STEP 6: GPT-5 TACTICAL PLANNING');
console.log('   🧠 Model: gpt-5-preview (Planner)');
console.log('   📤 Input: Claude strategy + venue catalog');
console.log('   📥 Output: ranked venues with timing & value scores');
console.log();

const rankingResult = await client.query(
  'SELECT * FROM rankings WHERE correlation_id = $1',
  [correlationId]
);

if (rankingResult.rows.length > 0) {
  const ranking = rankingResult.rows[0];
  console.log('🔷 STEP 6B: DB WRITE → rankings table');
  console.log('   💾 Table: rankings');
  console.log('   ✅ Record:', {
    ranking_id: ranking.ranking_id,
    correlation_id: ranking.correlation_id,
    snapshot_id: ranking.snapshot_id
  });
  console.log();

  // 4. Check ranking_candidates table
  console.log('🔷 STEP 7: DB WRITE → ranking_candidates table');
  const candidatesResult = await client.query(
    'SELECT * FROM ranking_candidates WHERE ranking_id = $1',
    [ranking.ranking_id]
  );
  
  console.log(`   💾 Table: ranking_candidates (${candidatesResult.rows.length} records)`);
  if (candidatesResult.rows.length > 0) {
    const first = candidatesResult.rows[0];
    console.log('   ✅ First Candidate:', {
      name: first.name,
      place_id: first.place_id,
      lat: first.lat,
      lng: first.lng,
      estimated_distance_miles: first.estimated_distance_miles,
      drive_time_minutes: first.drive_time_minutes,
      distance_source: first.distance_source
    });
  }
  console.log();
} else {
  console.warn('⚠️ No ranking found in database');
  console.log();
}

// 5. Display Routes API enrichment
console.log('🔷 STEP 8: GOOGLE ROUTES API ENRICHMENT');
console.log('   📡 Google Routes API: traffic-aware distance & ETA');
console.log(`   📤 Input: origin (${LAT}, ${LNG}) → destination coords`);
console.log('   📥 Output: estimated_distance_miles, driveTimeMinutes');
console.log();

console.log('🔷 STEP 9: GEMINI 2.5 PRO JSON VALIDATION');
console.log('   🧠 Model: gemini-2.5-pro (Validator)');
console.log('   📤 Input: GPT-5 ranking + Routes API data');
console.log('   📥 Output: validated JSON with ≥6 venues');
console.log();

// 6. Display final blocks
console.log('🔷 STEP 10: FINAL BLOCKS TO UI');
console.log(`   📦 ${blocks.length} venues ready for display`);
console.log();

blocks.forEach((block, i) => {
  console.log(`   ${i + 1}. ${block.name}`);
  console.log(`      Distance: ${block.estimated_distance_miles} mi`);
  console.log(`      Drive Time: ${block.driveTimeMinutes} min`);
  console.log(`      Value/Min: $${block.value_per_min?.toFixed(2) || '0.00'}`);
  console.log(`      Grade: ${block.value_grade || 'N/A'}`);
  console.log(`      Earnings: $${block.estimatedEarningsPerRide || 0}`);
  console.log();
});

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('✅ WORKFLOW COMPLETE');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

await client.end();
process.exit(0);
