import credentials from 'src/environments/.cred'
/* ✅TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  //✅TODO setup auth0 env
  auth0: {
    url: credentials.url, // the auth0 domain prefix
    audience: credentials.audience, // the audience set for the auth0 app
    clientId: credentials.id, // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
