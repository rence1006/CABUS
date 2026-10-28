export function emptyData(){return {tasks:[],goals:[],expenses:[],workouts:[],budgets:{},reminders:[],draft:null,imports:[]};}
const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function requireValue(condition,message){if(!condition)throw new Error(message);}
function text(value,label,max=250,allowEmpty=false){requireValue(typeof value==='string'&&value.length<=max&&(allowEmpty||value.trim().length>0),`Invalid ${label}.`);}
export function validDate(value){if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;const date=new Date(value+'T12:00:00Z');return !Number.isNaN(date.getTime())&&date.toISOString().slice(0,10)===value;}
function number(value,label,min=0,max=10000000,integer=false){requireValue(typeof value==='number'&&Number.isFinite(value)&&value>=min&&value<=max&&(!integer||Number.isInteger(value)),`Invalid ${label}.`);}
function money(value){number(value,'amount');requireValue(Math.abs(value*100-Math.round(value*100))<0.000001,'Amounts can have at most two decimal places.');}
function list(value,label,limit=2000){requireValue(Array.isArray(value)&&value.length<=limit,`Invalid ${label} list.`);return value;}
function unique(list){const ids=new Set();for(const record of list){requireValue(object(record),'Invalid record.');text(record.id,'record ID',100);requireValue(!ids.has(record.id),'Duplicate record ID.');ids.add(record.id);}}
function exercise(e){requireValue(object(e),'Invalid exercise.');text(e.name,'exercise name',120);number(e.sets,'sets',1,10000,true);number(e.reps,'reps',1,10000,true);number(e.weight,'weight',0,100000);}
function workout(w,draft=false){requireValue(object(w),'Invalid workout.');text(w.title,'workout name',120);requireValue(validDate(w.date),'Invalid workout date.');list(w.exercises,'exercises',200).forEach(exercise);if(draft){requireValue(typeof w.startedAt==='string'&&!Number.isNaN(Date.parse(w.startedAt)),'Invalid workout start.');}else{number(w.minutes,'duration',1,1440,true);requireValue(w.exercises.length>0,'Add at least one exercise.');}}
export function validateData(input){
 requireValue(object(input),'Invalid tracker data.');
 const expected=Object.keys(emptyData());requireValue(Object.keys(input).every(k=>expected.includes(k)),'Unknown tracker data field.');
 for(const key of ['tasks','goals','expenses','workouts','reminders'])unique(list(input[key],key));
 for(const t of input.tasks){text(t.title,'task title',120);requireValue(['Work','Personal','Shopping','Health','Study'].includes(t.category),'Invalid task category.');requireValue(['Low','Medium','High'].includes(t.priority),'Invalid priority.');requireValue(['Pending','In Progress','Completed'].includes(t.status),'Invalid task status.');requireValue(validDate(t.deadline),'Invalid task date.');}
 for(const g of input.goals){text(g.title,'goal title',120);text(g.description,'goal description',2000,true);requireValue(['short-term','long-term'].includes(g.type),'Invalid goal type.');requireValue(validDate(g.deadline),'Invalid goal date.');for(const m of list(g.milestones,'milestones',200)){requireValue(object(m),'Invalid milestone.');text(m.text,'milestone',250);requireValue(typeof m.done==='boolean','Invalid milestone completion.');}}
 for(const e of input.expenses){text(e.description,'expense description',120);money(e.amount);requireValue(e.amount>0,'Expense amount must be positive.');requireValue(validDate(e.date),'Invalid expense date.');requireValue(['Food','Transport','Shopping','Entertainment','Bills','Health','Other'].includes(e.category),'Invalid expense category.');}
 input.workouts.forEach(w=>workout(w));
 requireValue(object(input.budgets),'Invalid budgets.');requireValue(Object.keys(input.budgets).length<=240,'Too many budget months.');for(const [month,value]of Object.entries(input.budgets)){requireValue(/^\d{4}-(0[1-9]|1[0-2])$/.test(month),'Invalid budget month.');money(value);}
 for(const r of input.reminders){text(r.text,'reminder',500);requireValue(typeof r.done==='boolean','Invalid reminder completion.');}
 if(input.draft!==null)workout(input.draft,true);
 const digests=new Set();for(const receipt of list(input.imports,'import receipts',500)){requireValue(object(receipt)&&typeof receipt.digest==='string'&&/^[a-f0-9]{64}$/.test(receipt.digest),'Invalid import digest.');requireValue(!digests.has(receipt.digest),'Duplicate import receipt.');digests.add(receipt.digest);text(receipt.filename,'import filename',250);requireValue(typeof receipt.importedAt==='string'&&!Number.isNaN(Date.parse(receipt.importedAt)),'Invalid import date.');}
 return input;
}
