<script lang="ts">
    import Select from "svelte-select"
    import { _ } from 'svelte-i18n';
    import {onMount} from "svelte";
    import Papa from "papaparse";

    let items;
    const default_value = {label:'Aucun',value:-1} ;

    export let value;

    onMount(async () => {
        const res = await fetch("./electrical_foot_print.csv");
        const text = await res.text();
        items = toSelectItems(text)
        console.log(items)
        value = items.filter((item)=>item['value']===default_value['value'])[0]
    });

    function toSelectItems(csv) {
        const csvParsed = Papa.parse(csv,{header:true, dynamicTyping: true})
        const rowData = csvParsed.data;
        console.log(rowData)
        const selectItems = []
        selectItems.push(default_value)
        return selectItems.concat(rowData.map((row) => {
            return {
                label: row['country'],
                value: row['gwp_emission_factor']
            }}))
    }
</script>

<div>
{$_('index.select_country_elec_impact')}
<Select {items} bind:value={value} ></Select>
</div>

