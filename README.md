# Verify Custom BlueSky Handles With CloudFlare Worker

BlueSky gives you a couple of options to validate an account using your own domain/subdomain. One option is to create a TXT DNS record with your DID (BlueSky account unique id) and the other option is to respond to a request to https://${handle}/.well-known/atproto-did with the handle's did.

Creating TXT DNS records can get pretty out of hand if you have many users/subdomains for the same domain. So, I created a simple CloudFlare worker that uses a D1 database that can respond with the correct DID when https://${handle}/.well-known/atproto-did is routed to one of my domains.

To make things even easier, I created a python script to manage the D1 database. This way, there is no need to login to ClodFlare to add more BlueSky handles to the D1 database.

## How it Works

This tool assumes that you have a CloudFlare account and that the traffic for your domain is being proxied by ClouFlare.

Create a CloudFlare D1 database with only 2 columns: ```handle``` and ```did```. You can use the Python script to manage this.

Setup a CloudFlare worker with the code from ```worker.js``` .

Add a worker route to each domain that should be using the worked. I added a wildcard route so I can validate all subdomains with the
same route.

## Step by Step

### Enable CloudFlare API for D1 storage

You can skip this step if you prefer to maintain the table manually through CloudFlare's web interface.

Login to CloudFlare and go to ```Manage Account > Account API Tokens```. Create a new token with Account permissions and ```D1``` service. Make sure to select ```Edit``` access.

Make sure to copy and save the token in a safe place.

### Create a D1 Database

While you are still logged in to CloudFlare, go to the ```Workers and Pages > D1 SQL Database``` page and create a new database. To make things easier, you can call the database ```atproto```. Create a table in this database named ```atproto_did```. This table should have two columns: ```handle``` and ```did```.

You can start adding handles and DIDs to the table using the web interface, or you can use the Python scrip from this repo to manage the table.

### Create a CloudFlare Worker

While you are still logged in to CloudFlare, go to the ```Workers and Pages``` tab. Use the create button to create a new worker.

Use the code from ```worker.js``` on this repository to replace the default worker code CloudFlare gives you.

Make sure to edit the code if you created a database or a table with a different name than suggested above.

```javascript
export default {
    async fetch(request, env, ctx) {

        const url = new URL(request.url);
        
        // atproto_db is the database being used by the worker.
        // atproto_did is the table being used by the worker.
        // the table should have a column named 'handle'
        // Change this accordingly
        const { results } = await env.atproto_db.prepare(
            "SELECT did FROM atproto_did WHERE handle = ?",
        )
            .bind(url.hostname)
            .all();
        
        if(results.length){
            
            // This assumes that the table has a column named 'did'
            return new Response(results[0]['did'])
    
        }
    
        return new Response('Why are you here?');
    },
  };
```

Go to the Worker's ```Settings``` tab and add an item under ```Domains & Routes```. Add a new ```Route``` by selecting the domain you are using from the options under ```Zone``` and add a wildcard route so all requests to ```*.domain.com/.well-known/atproto-did``` are routed to the worker.

Still in the Worker's ```Settings``` tab, add your newly created database under the ```Bindings``` section. This will allow the worker to connect to the database.

###
