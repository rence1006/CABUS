import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
export function createDatabase(filename) {
 const db=new DatabaseSync(filename);
 db.exec('PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;');
 db.exec(readFileSync(new URL('../migrations/0001.sql',import.meta.url),'utf8'));
 const make=(sql,values=[])=>({sql,values,bind(...args){return make(sql,args);},async first(){return db.prepare(sql).get(...values)||null;},async all(){return {results:db.prepare(sql).all(...values)};},async run(){const result=db.prepare(sql).run(...values);return {success:true,meta:{changes:Number(result.changes)}};}});
 return {prepare:sql=>make(sql),async batch(statements){db.exec('BEGIN IMMEDIATE');try{const results=statements.map(s=>({success:true,meta:{changes:Number(db.prepare(s.sql).run(...s.values).changes)}}));db.exec('COMMIT');return results;}catch(error){db.exec('ROLLBACK');throw error;}},close(){db.close();}};
}
