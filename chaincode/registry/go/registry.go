/*
Copyright IBM Corp. 2016 All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

		 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

//Off Chain Trusted Compute Service Work Registry Chaincode
import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

var logger = shim.NewLogger("WorkerRegistry")

const (
	WORKERACTIVE         = 1
	WORKEROFFLINE        = 2
	WORKERDECOMMISSIONED = 3
	WORKERCOMPROMISED    = 4

	OBJECTTYPE   = "WorkerRegister"
	PAGESIZE     = 10
	UINT64FORMAT = "%020d"
	BYTE32FORMAT = "%032s"
)

// WorkerRegisterParam workerRegister invocation parameter
type WorkerRegisterParam struct {
	WorkerID          string   `json:"workerID"`
	WorkerType        uint64   `json:"workerType"`
	OrganizationID    string   `json:"organizationID"`
	ApplicationTypeId []string `json:"applicationTypeId,omitempty"`
	Details           string   `json:"details"`
	Status            uint64   `json:"status,omitempty"`
}

// WorkerLookUpParam workerLookUp invocation parameter
type WorkerLookUpParam struct {
	WorkerType        uint64 `json:"workerType,omitempty"`
	OrganizationID    string `json:"organizationID,omitempty"`
	ApplicationTypeId string `json:"applicationTypeId,omitempty"`
}

type WorkerLookUpResParam struct {
	TotalCount uint64   `json:"totalCount"`
	LookupTag  string   `json:"lookupTag"`
	IDs        []string `json:"ids,omitempty"`
}

// WorkerRegistry Chaincode struct
// This chaincode allows application to register, lookup and retrieve workers
type WorkerRegistry struct {
}

// Init the init function of the chaincode
func (t *WorkerRegistry) Init(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("WorkerRegistry Init")
	return shim.Success(nil)
}

// WorkerRegister - This function registers a Worker
// params:
//   byte32 workerID
//   uint256 workerType
//   bytes32 organizationID
//   bytes32[] applicationTypeId
//   string details
// returns:
func (t *WorkerRegistry) workerRegister(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerRegister")
	if args != nil {
		logger.Info(args)
	}

	var param WorkerRegisterParam
	value := []byte(args[0])
	err := json.Unmarshal(value, &param)
	if err != nil {
		logger.Errorf("Error trying to decode passed in parameters: %s", err)
		return shim.Error(err.Error())
	}

	// Set default status to be active
	param.Status = WORKERACTIVE

	//Serialize the value
	value, err = json.Marshal(param)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Infof("The worker ID: %s", param.WorkerID)
	err = stub.PutState(param.WorkerID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Need to add compositeKey so that the search would work
	// The composite key is made of OBJECTTYPE, workerType, organizationID and appTypeID
	compValue := []byte(param.WorkerID)
	for _, appTypeID := range param.ApplicationTypeId {
		key1 := fmt.Sprintf(UINT64FORMAT, param.WorkerType)
		key2 := fmt.Sprintf(BYTE32FORMAT, param.OrganizationID)
		key3 := fmt.Sprintf(BYTE32FORMAT, appTypeID)
		key4 := fmt.Sprintf(BYTE32FORMAT, param.WorkerID)
		compKey, err := stub.CreateCompositeKey(OBJECTTYPE,
			[]string{key1, key2, key3, key4})
		if err != nil {
			return shim.Error(err.Error())
		}
		logger.Infof("The composite key: %s, length: %d", compKey, len(compKey))
		err = stub.PutState(compKey, compValue)
		if err != nil {
			return shim.Error(err.Error())
		}
	}

	// Handling payload for the event, since payload is omited by
	// fabric python sdk, workID is simply put in the event, this
	// need to be revisted once python sdk support payload
	eventData := map[string]interface{}{"workerID": param.WorkerID}
	eventPayload, err := json.Marshal(eventData)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.SetEvent("workerRegistered", eventPayload)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished WorkerRegister")
	return shim.Success(nil)
}

// WorkerLookUp - This function retrieves a list of Worker ids that match input
// parameter. The Worker must match to all input parameters (AND mode) to be
// included in the list.
// params:
//   uint8 workerType
//   bytes32 organizationId
//   bytes32 applicationTypeId
// returns:
//   int totalCount
//   string LookupTag
//   bytes32[] ids
func (t *WorkerRegistry) workerLookUp(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerLookUp")
	if args != nil {
		logger.Info(args)
	}

	var param WorkerLookUpParam
	value := []byte(args[0])
	err := json.Unmarshal(value, &param)
	if err != nil {
		logger.Errorf("Error trying to decode passed in parameters: %s", err)
		return shim.Error(err.Error())
	}

	attrs := []string{}
	if param.WorkerType != 0 {
		attrs = append(attrs, fmt.Sprintf(UINT64FORMAT, param.WorkerType))
		if param.OrganizationID != "0" {
			attrs = append(attrs, fmt.Sprintf(BYTE32FORMAT, param.OrganizationID))
			if param.ApplicationTypeId != "0" {
				attrs = append(attrs, fmt.Sprintf(BYTE32FORMAT, param.ApplicationTypeId))
			}
		}
	}
	logger.Infof("The search starting key: %v", attrs)

	iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(OBJECTTYPE, attrs,
		int32(PAGESIZE+1), "")
	if err != nil {
		logger.Errorf("Error trying to query with partial composite key: %s", err)
		return shim.Error(err.Error())
	}

	var resparam WorkerLookUpResParam
	for iter.HasNext() {
		item, _ := iter.Next()
		logger.Infof("The value: %v", item)
		resparam.IDs = append(resparam.IDs, string(item.Value))
		if len(resparam.IDs) > PAGESIZE {
			resparam.TotalCount = PAGESIZE + 1
			break
		} else {
			resparam.TotalCount += 1
		}
	}
	logger.Info("Result metadata: %v", metadata)

	//Serialize the response
	value, err = json.Marshal(resparam)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// WorkerLookUpNext - This function is called to retrieve additional results of the
// Worker lookup initiated byworkerLookUp call.
// params:
//   uint8 workerType
//   bytes32 organizationId
//   bytes32 applicationTypeId
//   string lookUpTag
// returns:
//   int totalCount
//   string newLookupTag
//   bytes32[] ids
func (t *WorkerRegistry) workerLookUpNext(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerLookUpNext")

	return shim.Success(nil)
}

// WorkerRetrieve - This function retrieves information for the Worker and it can be
// called from any authorized publickey (Ethereum address) or DID
// params:
//   byte32 workerId
// returns:
//   uint8 workerType
//   string workerTypeDataUri
//   bytes32 organizationId
//   bytes32[] applicationTypeId
func (t *WorkerRegistry) workerRetrieve(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerRetrieve")

	return shim.Success(nil)
}

// query - This function retrieves information by worker id
// params:
//   byte32 workerId
// returns:
//   uint8 workerType
//   string workerTypeDataUri
//   bytes32 organizationId
//   bytes32[] applicationTypeId
func (t *WorkerRegistry) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("query")

	// Get the state from the ledger
	logger.Infof("query workID: %s", args[0])
	Avalbytes, err := stub.GetState(args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	if Avalbytes == nil {
		return shim.Error("WorkerID '" + args[0] + "' does not exist")
	}

	return shim.Success(Avalbytes)
}

// Invoke - this function simply satisfy the main requirement of chaincode
func (t *WorkerRegistry) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "workerRegister" {
		return t.workerRegister(stub, args)
	} else if function == "workerLookUp" {
		return t.workerLookUp(stub, args)
	} else if function == "workerLookUpNext" {
		return t.workerLookUpNext(stub, args)
	} else if function == "workerRetrieve" {
		return t.workerRetrieve(stub, args)
	} else if function == "query" {
		return t.query(stub, args)
	}

	return shim.Error("Invalid invoke function name")
}

func main() {
	err := shim.Start(new(WorkerRegistry))
	if err != nil {
		logger.Errorf("Error starting Simple chaincode: %s", err)
	}
}
