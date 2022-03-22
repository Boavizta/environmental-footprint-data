<script lang="ts">
    import  {Select} from "svelte-select"
    let region = "eu"

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

<Select {items} {value} on:select={handleSelect}></Select>