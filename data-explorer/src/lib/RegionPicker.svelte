<script lang="ts">
    import  {Select} from "svelte-select"
    export let region = "EU";
    import { _ } from 'svelte-i18n';

    onMount(async () => {
        const res = await fetch("./electrical_foot_print.csv");
        const text = await res.text();
    });


    let items = [
        {value: 'chocolate', label: 'Chocolate'},
        {value: 'pizza', label: 'Pizza'},
        {value: 'cake', label: 'Cake'},
        {value: 'chips', label: 'Chips'},
        {value: 'ice-cream', label: 'Ice Cream'},
    ];

    let value = {value: 'cake', label: 'Cake'};

    function handleSelect(event) {
    }


</script>

{$_('index.select_location')}
<input name="region" type="text" bind:value={region}>
<!--
<Select {items} {value} on:select={handleSelect}></Select>
-->
