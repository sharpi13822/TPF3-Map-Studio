class ExportManager {


    constructor() {


    }



    export(data, filename = "tpf2-export.json") {


        const json =

            JSON.stringify(
                data,
                null,
                4
            );



        const blob =

            new Blob(
                [json],
                {
                    type: "application/json"
                }
            );



        const url =

            URL.createObjectURL(
                blob
            );



        const link =

            document.createElement(
                "a"
            );


        link.href = url;


        link.download = filename;


        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);

        setTimeout(() => URL.revokeObjectURL(url), 10000);


    }


}