const axios     = require('axios')
const AWS       = require('aws-sdk')
const converter = AWS.DynamoDB.Converter.unmarshall

const host    = process.env.ENDPOINT
const index   = process.env.INDEX
const url     = `https://${host}/${index}/_doc`
const headers = { 'Content-Type': 'application/json' }

exports.handler = async event => {
    await Promise.all(event.Records.map(record => {
        const partitionKey = record.dynamodb.Keys.partitionKey.S
        const rangeKey = record.dynamodb.Keys.rangeKey.S
        const itemUrl = `${url}/${partitionKey}_${rangeKey}`

        if (record.eventName === 'REMOVE') {
            return axios.delete(itemUrl)
        } else {
            let document = converter(record.dynamodb.NewImage)
            document = removeTechnicalFields(document)
            return axios.put(
                itemUrl,
                JSON.stringify(document),
                { headers }
            )
        }
    }))
}

const removeTechnicalFields = (body) => {
  delete body.SequenceNumber
  delete body.SizeBytes
  delete body.StreamViewType
  delete body['aws:rep:deleting']
  delete body['aws:rep:updatetime']
  delete body['aws:rep:updateregion']
  return body
}
