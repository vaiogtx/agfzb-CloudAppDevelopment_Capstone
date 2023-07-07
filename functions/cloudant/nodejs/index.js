// Code for action: get-dealership
async function main(params) {
	const { CloudantV1 } = require("@ibm-cloud/cloudant");
	const { IamAuthenticator } = require("ibm-cloud-sdk-core");
	const authenticator = new IamAuthenticator({
		apikey: params.IAM_API_KEY
	});
	const cloudant = CloudantV1.newInstance({
		authenticator: authenticator
	});
	cloudant.setServiceUrl(params.COUCH_URL);

	try {
		if (params.st) {
			const result = await findDealershipByState(cloudant, params.st);
			const code = result.length ? 200 : 404;
			return {
				statusCode: code,
				headers: { "Constent-Type": "application/json" },
				body: result
			};
		} else if (params.id) {
			const result = await findDealershipById(cloudant, params.id);
			const code = result.length ? 200 : 404;
			return {
				statusCode: code,
				headers: { "Constent-Type": "application/json" },
				body: result
			};
		} else {
			const result = await findAllDealerships(cloudant);
			const code = result.length ? 200 : 400;
			return {
				statusCode: code,
				headers: { "Constent-Type": "application/json" },
				body: result
			};
		}
	} catch (err) {
		console.log(err);
		return {
			statusCode: 500,
			headers: { "Constent-Type": "application/json" },
			body: { "error": "Internal Server Error" }
		};
	}
}

async function findDealershipByState(cloudant, state) {
	const result = await cloudant.postFind({ db: "dealerships", selector: { st: state } });
	return result.result.docs;
}

async function findDealershipById(cloudant, id) {
	const result = await cloudant.postFind({ db: "dealerships", selector: { id: parseInt(id) } });
	return result.result.docs;
}

async function findAllDealerships(cloudant) {
	const result = await cloudant.postAllDocs({ db: "dealerships", includeDocs: true, limit: 10 });
	return result.result.rows;
}