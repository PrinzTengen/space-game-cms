Segmented control for filters and language.

```jsx
<Segment label="Beiträge filtern" value="all" onChange={setF}
  options={[{value:'all',label:'Alle',count:5},{value:'news',label:'News',count:2},{value:'devlog',label:'Devlogs',count:3}]} />
<Segment bare size="sm" value="de" options={[{value:'de',label:'DE',lang:'de'},{value:'en',label:'EN',lang:'en'}]} />
```
