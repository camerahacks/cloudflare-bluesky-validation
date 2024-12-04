/**
 * Worker to return the correct BlueSky ATProto Did for a given account
 *
 */

export default {
    async fetch(request, env, ctx) {
        
        // Create a URL object. This will make it easier to check the
        // domain without pattern matching
        const url = new URL(request.url);
        
        // atproto_db is the database being used by the worker. Change this accordingly
        // atproto_did is the table being used by the worker. Change this accordingly
        // the table should have a column named 'handle'
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