/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package arq.examples.update;

import org.apache.jena.riot.Lang ;
import org.apache.jena.riot.RDFDataMgr ;

import com.hp.hpl.jena.sparql.sse.SSE ;
import com.hp.hpl.jena.update.* ;

/** Simple example of SPARQL/Update : read a update script from a file and execute it */ 
public class UpdateReadFromFile
{
    public static void main(String []args)
    {
        // Create an empty GraphStore (has an empty default graph and no named graphs) 
        GraphStore graphStore = GraphStoreFactory.create() ;
        
        // ---- Read and update script in one step.
        UpdateAction.readExecute("update.ru", graphStore) ;
        
        // ---- Reset.
        UpdateAction.parseExecute("DROP ALL", graphStore) ;
        
        // ---- Read the update script, then execute, in separate two steps
        UpdateRequest request = UpdateFactory.read("update.ru") ;
        UpdateAction.execute(request, graphStore) ;

        // Write in debug format.
        System.out.println("# Debug format");
        SSE.write(graphStore) ;
        
        System.out.println();
        
        System.out.println("# N-Quads: S P O G") ;
        RDFDataMgr.write(System.out, graphStore, Lang.NQUADS) ;
    }
}
